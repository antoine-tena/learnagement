"""L'instance dans son ensemble : changer d'environnement, repartir de zéro, exporter, importer."""

import logging
import os
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import dotenv

from launcher import db, docker
from launcher.config import GREEN, NC, RED, YELLOW
from launcher.env import (
    ENV_FILE,
    apply_env_file,
    env_file_of,
    load_env,
    load_env_file,
    propagate_env,
    remove_env_files,
    save_env_file,
)

logger = logging.getLogger(__name__)

CONFIRM_RESET = (
    "Are you sure (YES/NO)? NO INITIAL DATA OR CUSTOMIZED CONFIGURATION CAN BE RECOVERED! "
)
CONFIRM_RESET_AGAIN = "Are you realy sure(YES/NO)? don't cry if you've lost anything! "


def is_running() -> bool:
    project = os.environ.get("COMPOSE_PROJECT_NAME")
    return bool(project) and docker.is_compose_running(project)


def switch_env(env: str) -> None:
    """Applique un environnement à l'instance, sans redemander ses secrets."""
    load_env(env)
    if os.environ.get("ENV") == env:
        return
    logger.info("%sSwitch to env: %s%s", GREEN, env, NC)
    docker.COMPOSE_FILE.unlink(missing_ok=True)
    save_env_file(apply_env_file(load_env_file(ENV_FILE), env_file_of(env)), ENV_FILE)
    propagate_env()
    dotenv.load_dotenv(ENV_FILE, override=True)


def reset() -> None:
    dotenv.load_dotenv()
    if is_running():
        logger.warning("%sInstance running, it cannot be reset from scratch%s", YELLOW, NC)
        return

    logger.warning("%sClean up App from scratch%s", RED, NC)
    logger.warning("%sThe application must be stopped%s", RED, NC)
    if input(CONFIRM_RESET) != "YES" or input(CONFIRM_RESET_AGAIN) != "YES":
        return

    project = os.environ["COMPOSE_PROJECT_NAME"]
    volume = f"{project}_learnagement_persistent_db_{os.environ['INSTANCE_NAME']}"
    try:
        subprocess.run([*docker.docker_command(), "volume", "rm", volume], check=True)
    except subprocess.CalledProcessError:
        logger.exception("Volume %s not removed", volume)

    shutil.rmtree(db.DATA_DIR, ignore_errors=True)
    shutil.rmtree(db.INIT_DIR, ignore_errors=True)
    docker.COMPOSE_FILE.unlink(missing_ok=True)
    remove_env_files()
    logger.info("%sThe application was reset to its initial state.%s", GREEN, NC)


def export() -> None:
    """Archive la base, la compose et l'environnement ; l'archive contient les mots de passe."""
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    export_dir = Path(f"Learnagement_{os.environ['INSTANCE_NAME']}_{stamp}")
    export_dir.mkdir()
    try:
        db.backup(export_dir / "sql")
        shutil.copy(docker.COMPOSE_FILE, export_dir)
        shutil.copy(ENV_FILE, export_dir / "env")
        shutil.make_archive(str(export_dir), "zip", ".", str(export_dir))
    finally:
        shutil.rmtree(export_dir)


def import_archive(archive: Path) -> None:
    if is_running():
        logger.warning("%sInstance running, you cannot import new instance%s", YELLOW, NC)
        return

    import_dir = Path(archive.stem)
    shutil.unpack_archive(archive)
    shutil.copy(import_dir / "env", ENV_FILE)
    propagate_env()
    shutil.copy(import_dir / docker.COMPOSE_FILE.name, docker.DOCKER_DIR)
    db.DATA_DIR.mkdir(exist_ok=True)  # So that Learnagement does not ask for free data
    for sql_file in db.SQL_DIR.iterdir():
        sql_file.unlink()
    shutil.copytree(import_dir / "sql", db.SQL_DIR, dirs_exist_ok=True)
    shutil.rmtree(import_dir)
