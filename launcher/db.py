"""La base de l'instance : fichiers d'initialisation, administrateur, sauvegardes."""

import asyncio
import logging
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from launcher.config import GREEN, NC
from launcher.docker import docker_command

logger = logging.getLogger(__name__)

DB_DIR = Path("db")
INIT_DIR = DB_DIR / "docker-entrypoint-initdb.d"
SQL_DIR = DB_DIR / "sql"
DATA_DIR = DB_DIR / "data"
TRANSIENT_ERRORS = ("doesn't exist", "unknown database", "can't connect", "access denied")
DUMP_OPTIONS = (
    "--ignore-views",
    "--skip-comments",
    "--skip-extended-insert",
    "--no-tablespaces",
)

password_hash = PasswordHash((BcryptHasher(),))


def mysql_container() -> str:
    return f"learnagement_mysql_{os.environ['INSTANCE_NAME']}"


def _client_env() -> dict[str, str]:
    """L'environnement du client : `docker exec -e MYSQL_PWD` y lit le mot de passe."""
    return {**os.environ, "MYSQL_PWD": os.environ["MYSQL_USER_PASSWORD"]}


def _exec_in_mysql() -> list[str]:
    return [*docker_command(), "exec", "-i", "-e", "MYSQL_PWD", mysql_container()]


def prepare_init_files() -> None:
    """Copie les migrations dans le dossier lu par MySQL à sa première initialisation."""
    if INIT_DIR.exists():
        logger.info("%sDB already exist initialized!%s", GREEN, NC)
        return
    INIT_DIR.mkdir()
    for source in SQL_DIR.iterdir():
        if source.is_file():
            shutil.copy(source, INIT_DIR / source.name)


def prepare_initial_data() -> None:
    """Demande les données initiales au premier lancement, puis les copie pour MySQL."""
    if DATA_DIR.exists():
        logger.info("%sData already exist in 'db/data'!%s", GREEN, NC)
    else:
        DATA_DIR.mkdir()
        print(
            "If you want an initial data set, put it into 'db/data' folder "
            "with name matches with [0-9]*.sql."
        )
        print("Free data samples are available at 'db/freeData' folder.")
        input("Then press enter")
    subprocess.run([sys.executable, "insertPrivateData.py"], cwd=DB_DIR, check=True)


def create_administrator() -> None:
    """Crée le compte administrateur ; un compte déjà présent n'est pas une erreur."""
    hashed = password_hash.hash(os.environ["LEARNAGEMENT_ADMINISTRATOR_PASSWORD"])
    request = (
        "INSERT INTO `LNM_administratif`"
        "(`id_administratif`, `nom`, `prenom`, `mail`, `login`, `password`, `password_updated`) "
        "VALUES(NULL, 'Administrator', 'Administrator', 'administrator@lnm.fr', NULL, "
        f"'{hashed}', '0')"
    )
    result = subprocess.run(
        [
            *_exec_in_mysql(),
            "mysql",
            "-u",
            os.environ["MYSQL_USER_LOGIN"],
            os.environ["MYSQL_DB"],
            "-e",
            request,
        ],
        capture_output=True,
        text=True,
        env=_client_env(),
        check=False,
    )
    if result.returncode == 0:
        return
    error = result.stderr.strip()
    if "1062" in error or "Duplicate entry" in error:
        print("L'administrateur existe déjà, aucune action nécessaire.")
        return
    raise RuntimeError(error)


async def wait_for_mysql_healthy(timeout: int = 300, poll_interval: int = 2) -> None:
    """Attend que le conteneur MySQL soit 'healthy' selon son healthcheck."""
    container = mysql_container()
    command = [*docker_command(), "inspect", "--format={{.State.Health.Status}}", container]
    elapsed = 0
    while elapsed < timeout:
        result = await asyncio.to_thread(
            subprocess.run, command, capture_output=True, text=True, check=False
        )
        status = result.stdout.strip()
        if status == "healthy":
            return
        if status == "unhealthy":
            raise RuntimeError(f"Le conteneur {container} est en état 'unhealthy'")
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(f"Timeout : {container} n'est pas devenu 'healthy' après {timeout}s")


async def create_administrator_with_retry(max_retries: int = 10, retry_delay: int = 3) -> None:
    """Réessaie tant que la base répond par une erreur transitoire de démarrage."""
    last_error: RuntimeError | None = None
    for attempt in range(1, max_retries + 1):
        print("Tentative d'ajout de l'Administrateur")
        try:
            await asyncio.to_thread(create_administrator)
        except RuntimeError as error:
            if not any(known in str(error).lower() for known in TRANSIENT_ERRORS):
                raise
            last_error = error
            if attempt < max_retries:
                await asyncio.sleep(retry_delay)
        else:
            return
    raise RuntimeError(
        f"Échec de l'insertion de l'administrateur après {max_retries} tentatives. "
        f"Dernière erreur : {last_error}"
    )


def _dump(target: Path, *options: str) -> None:
    with target.open("wb") as file:
        subprocess.run(
            [
                *_exec_in_mysql(),
                "mysqldump",
                "-u",
                os.environ["MYSQL_USER_LOGIN"],
                *DUMP_OPTIONS,
                *options,
                os.environ["MYSQL_DB"],
            ],
            stdout=file,
            env=_client_env(),
            check=True,
        )


def backup(folder: Path) -> None:
    """Sauvegarde séparément la structure, les données et les triggers."""
    logger.info("%sBackUp DB%s", GREEN, NC)
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    subprocess.run(
        [*docker_command(), "exec", "-i", mysql_container(), "mysqld", "--version"],
        check=True,
    )
    _dump(folder / f"0_struct_{stamp}.sql", "--no-data", "--skip-triggers")
    _dump(folder / f"5_data_{stamp}.sql", "--no-create-info", "--skip-triggers")
    _dump(folder / f"99_trigger_{stamp}.sql", "--no-create-info", "--no-data")
