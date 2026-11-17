"""Le partage distant des sauvegardes, monté le temps d'une sauvegarde puis démonté."""

import logging
import os
import re
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from pathlib import Path

from launcher.config import NC, RED

logger = logging.getLogger(__name__)

TRUE_VALUES = ("1", "true", "yes", "y", "on", "oui")
DRIVE_LETTERS = "ZYXWVUTSRQPONMLKJIHGFED"


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name, "").strip()
    return value.lower() in TRUE_VALUES if value else default


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def guess_remote_type(remote: str) -> str:
    forced = os.environ.get("BACKUP_REMOTE_TYPE", "").strip().lower()
    if forced:
        return forced
    if remote.startswith("//"):
        return "cifs"
    if re.match(r"^[^@/\s]+@[^:/\s]+:", remote):
        return "sshfs"
    if re.match(r"^[^/\s:]+:/", remote):
        return "nfs"
    raise ValueError(
        f"Format de BACKUP_REMOTE_DIRECTORY non reconnu : '{remote}' "
        "(utiliser BACKUP_REMOTE_TYPE pour le préciser)"
    )


def _sudo() -> list[str]:
    return ["sudo", "-n"] if env_bool("BACKUP_REMOTE_SUDO") and os.geteuid() != 0 else []


def _cifs_credentials() -> tuple[str, Path | None]:
    """L'option de connexion cifs ; un fichier 0600 garde le mot de passe hors de `ps`."""
    user = os.environ.get("BACKUP_REMOTE_USER")
    if not user:
        return "guest", None
    fd, path = tempfile.mkstemp(prefix="learnagement_cred_")
    with os.fdopen(fd, "w") as credentials:
        password = os.environ.get("BACKUP_REMOTE_PASSWORD", "")
        credentials.write(f"username={user}\npassword={password}\n")
    return f"credentials={path}", Path(path)


def _mount_command(remote_type: str, remote: str, mount_point: str) -> list[str]:
    match remote_type:
        case "cifs" | "nfs":
            return [*_sudo(), "mount", "-t", remote_type, remote, mount_point]
        case "sshfs":
            return ["sshfs", remote, mount_point]
    raise ValueError(f"Type de montage non supporté : '{remote_type}'")


def _unmount(remote_type: str, mount_point: str) -> bool:
    """Démonte, paresseusement en dernier recours ; False si le point reste monté."""
    if remote_type == "sshfs":
        attempts = [["fusermount", "-u", mount_point], ["fusermount", "-uz", mount_point]]
    else:
        attempts = [[*_sudo(), "umount", mount_point], [*_sudo(), "umount", "-l", mount_point]]
    for command in attempts:
        completed = _run(command)
        if completed.returncode == 0:
            logger.info("Remote directory unmounted")
            return True
    logger.error("%sDémontage de %s impossible : %s%s", RED, mount_point, completed.stderr, NC)
    return False


@contextmanager
def _mount_unix(remote: str) -> Iterator[Path]:
    remote_type = guess_remote_type(remote)
    mount_point = tempfile.mkdtemp(prefix="learnagement_backup_")
    options = [os.environ.get("BACKUP_REMOTE_OPTIONS", "").strip()]
    credentials_file = None
    if remote_type == "cifs":
        credentials, credentials_file = _cifs_credentials()
        options.insert(0, credentials)
    command = _mount_command(remote_type, remote, mount_point)
    if any(options):
        command += ["-o", ",".join(option for option in options if option)]
    try:
        completed = _run(command)
        if completed.returncode != 0:
            raise RuntimeError(f"Montage de '{remote}' impossible : {completed.stderr.strip()}")
        logger.info("Remote directory mounted (%s) on %s", remote_type, mount_point)
        try:
            yield Path(mount_point)
        finally:
            if not _unmount(remote_type, mount_point):
                mount_point = ""  # un point encore monté n'est pas supprimé
    finally:
        if credentials_file:
            credentials_file.unlink(missing_ok=True)
        if mount_point:
            with suppress(OSError):
                os.rmdir(mount_point)


@contextmanager
def _mount_windows(remote: str) -> Iterator[Path]:
    """`net use` monte sur une lettre de lecteur libre, pas dans un répertoire."""
    if not remote.startswith("\\\\"):
        raise ValueError(
            "Sous Windows, BACKUP_REMOTE_DIRECTORY doit être un chemin UNC "
            f"(\\\\serveur\\partage), reçu : '{remote}'"
        )
    letter = next((drive for drive in DRIVE_LETTERS if not os.path.exists(f"{drive}:\\")), None)
    if letter is None:
        raise RuntimeError("Aucune lettre de lecteur disponible")
    command = ["net", "use", f"{letter}:", remote, "/persistent:no"]
    user = os.environ.get("BACKUP_REMOTE_USER")
    if user:
        command[4:4] = [os.environ.get("BACKUP_REMOTE_PASSWORD", ""), f"/user:{user}"]
    completed = _run(command)
    if completed.returncode != 0:
        raise RuntimeError(f"Montage de '{remote}' impossible : {completed.stderr.strip()}")
    logger.info("Remote directory mounted on %s:", letter)
    try:
        yield Path(f"{letter}:\\")
    finally:
        completed = _run(["net", "use", f"{letter}:", "/delete", "/y"])
        if completed.returncode != 0:
            logger.error("%sDémontage de %s: impossible : %s%s", RED, letter, completed.stderr, NC)


@contextmanager
def mounted_remote(remote: str) -> Iterator[Path]:
    with _mount_windows(remote) if os.name == "nt" else _mount_unix(remote) as path:
        yield path
