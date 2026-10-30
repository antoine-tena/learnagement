"""Les commandes du lanceur : `python Learnagement.py <commande>`."""

import asyncio
import logging
import os
import shutil
import signal
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import FrameType

import click
import dotenv
from click_default_group import DefaultGroup

from launcher import db, docker
from launcher.config import (
    GREEN,
    NC,
    RED,
    YELLOW,
    containers_dev,
    containers_prod,
    containers_system,
    envs,
)
from launcher.env import (
    apply_env_file,
    generate_base_env,
    load_env_file,
    propagate_env,
    save_env_file,
)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

ENV_CHOICES = click.Choice(sorted(envs))
ENV_HELP = "Environment to use: " + ", ".join(sorted(envs))
CONFIRM_RESET = (
    "Are you sure (YES/NO)? NO INITIAL DATA OR CUSTOMIZED CONFIGURATION CAN BE RECOVERED! "
)
CONFIRM_RESET_AGAIN = "Are you realy sure(YES/NO)? don't cry if you've lost anything! "


def _git_branch() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _security_check() -> None:
    branch = _git_branch()
    env = os.environ["ENV"]
    if branch == "main" and env != "prod":
        logger.error(
            "%sSECURITY ALERT: App run from main branch without 'ENV' "
            "environment variable set as 'prod'%s",
            RED,
            NC,
        )
        sys.exit(1)
    if branch == "prerelease" and env != "prod":
        logger.warning(
            "%sSECURITY WARNING: App run from prerelease branch without 'ENV' "
            "environment variable set as 'prod'%s",
            YELLOW,
            NC,
        )
    else:
        logger.info("%sApp run from '%s' branch with '%s' environment%s", GREEN, branch, env, NC)


def _generate_env(env: str = "dev") -> None:
    if not Path(".env").exists():
        for name in ("dev", "prod"):
            if not Path(f".env_{name}.env").exists():
                shutil.copy(f"config/env.{name}", f".env_{name}.env")

        logger.warning(
            "%senv file doesn't exist, generate it with '%s' environnement %s", YELLOW, env, NC
        )
        env_vars = generate_base_env()
        if not Path(f".env_{env}.env").exists():
            logger.error("%sSpecific env file '.env_%s.env' doesn't exist%s", RED, env, NC)
            sys.exit(1)
        save_env_file(apply_env_file(env_vars, f".env_{env}.env"), ".env")

    propagate_env()
    dotenv.load_dotenv()


def _switch_env(env: str) -> None:
    """Applique un environnement à l'instance et oublie le compose qui en dépendait."""
    _generate_env()
    logger.info("%sSwitch to env: %s%s", GREEN, env, NC)
    docker.COMPOSE_FILE.unlink(missing_ok=True)
    env_file = ".env_prod.env" if env == "prod" else ".env_dev.env"
    save_env_file(apply_env_file(load_env_file(".env"), env_file), ".env")
    propagate_env()


def _reset_instance() -> None:
    dotenv.load_dotenv()
    project = os.environ["COMPOSE_PROJECT_NAME"]
    if docker.is_compose_running(project):
        logger.warning("%sInstance running, it cannot be reset from scratch%s", YELLOW, NC)
        return

    logger.warning("%sClean up App from scratch%s", RED, NC)
    logger.warning("%sThe application must be stopped%s", RED, NC)
    if input(CONFIRM_RESET) != "YES" or input(CONFIRM_RESET_AGAIN) != "YES":
        return

    volume = f"{project}_learnagement_persistent_db_{os.environ['INSTANCE_NAME']}"
    try:
        subprocess.run([*docker.docker_command(), "volume", "rm", volume], check=True)
    except subprocess.CalledProcessError:
        logger.exception("Volume %s not removed", volume)

    shutil.rmtree(db.DATA_DIR, ignore_errors=True)
    shutil.rmtree(db.INIT_DIR, ignore_errors=True)
    generated = [docker.COMPOSE_FILE, Path(".env"), Path(".env_dev.env"), Path(".env_prod.env")]
    containers = containers_system + containers_dev + containers_prod
    for path in [*generated, *(Path(container) / ".env" for container in containers)]:
        path.unlink(missing_ok=True)
    logger.info("%sThe application was reset to its initial state.%s", GREEN, NC)


async def _setup_administrator() -> None:
    await db.wait_for_mysql_healthy()
    await db.create_administrator_with_retry()
    logger.info("%sWeb Apps will run on: %s%s", GREEN, os.environ["INSTANCE_URL"], NC)
    logger.info(
        "%sPHPMyAdmin will run on: http://127.0.0.1:%s%s",
        GREEN,
        os.environ["PHPMYADMIN_PORT"],
        NC,
    )


async def _run_instance(options: list[str]) -> None:
    """Lance compose et prépare l'administrateur en parallèle : `up` peut rester au premier plan."""
    up = asyncio.create_task(asyncio.to_thread(docker.compose_up, options))
    setup = asyncio.create_task(_setup_administrator())
    await asyncio.wait({up, setup}, return_when=asyncio.FIRST_EXCEPTION)
    for task in (up, setup):
        if task.done() and task.exception() is not None:
            setup.cancel()
            raise task.exception()
    await asyncio.gather(up, setup)


def _start(options: list[str]) -> None:
    dotenv.load_dotenv()
    project = os.environ.get("COMPOSE_PROJECT_NAME")
    if project and docker.is_compose_running(project):
        logger.warning("%sInstance already running%s", YELLOW, NC)
        return

    _generate_env()
    db.prepare_init_files()
    db.prepare_initial_data()
    docker.write_compose_file()
    _security_check()
    asyncio.run(_run_instance(options))


@click.group(cls=DefaultGroup, default="start", default_if_no_args=True)
def cli() -> None:
    pass


@cli.command(help="Generate environment without starting the application")
@click.option("--env", type=ENV_CHOICES, default="dev", help=ENV_HELP)
def generate_env(env: str) -> None:
    _generate_env(env)


@cli.command(help="Start the application")
@click.option("--docker_option", default=None, help="See docker compose options")
@click.option("--restart", is_flag=True, help="Restart the application")
@click.option("--rebuild", is_flag=True, help="Rebuild Docker images")
@click.option("--test", is_flag=True, help="Test options without starting the application")
@click.option(
    "--from_scratch", is_flag=True, help="Reset the application to its initial state (IRREVERSIBLE)"
)
@click.option(
    "--env",
    type=ENV_CHOICES,
    default=None,
    help="Environment to use, (use previously used if not set)",
)
def start(
    docker_option: str | None,
    restart: bool,
    rebuild: bool,
    test: bool,
    from_scratch: bool,
    env: str | None,
) -> None:
    options = docker.parse_docker_options(docker_option)
    if restart:
        if test:
            logger.warning("%sYou cannot test restart.%s", YELLOW, NC)
            return
        logger.warning("%sRestart sometimes unstable.%s", YELLOW, NC)
        dotenv.load_dotenv()
        docker.compose_down()

    if from_scratch:
        _reset_instance()

    if env:
        _switch_env(env)
        rebuild = True

    if test:
        return
    _start(["--build", *options] if rebuild else options)


@cli.command(name="backupdb", help="Backup the database (structure, data and triggers)")
@click.option("--backup_folder", default="db/backup", type=click.Path(path_type=Path))
def backup_db(backup_folder: Path) -> None:
    dotenv.load_dotenv()
    db.backup(backup_folder)


@cli.command(name="exportinstance", help="Export the current instance as a zip archive")
def export_instance() -> None:
    dotenv.load_dotenv()
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    export_dir = Path(f"Learnagement_{os.environ['INSTANCE_NAME']}_{stamp}")
    export_dir.mkdir()
    try:
        db.backup(export_dir / "sql")
        shutil.copy(docker.COMPOSE_FILE, export_dir)
        shutil.copy(".env", export_dir / "env")
        shutil.make_archive(str(export_dir), "zip", ".", str(export_dir))
    finally:
        shutil.rmtree(export_dir)


@cli.command(help="Import an instance from a zip archive")
@click.option("--file", "archive", required=True, type=click.Path(exists=True, path_type=Path))
def import_instance(archive: Path) -> None:
    dotenv.load_dotenv()
    project = os.environ.get("COMPOSE_PROJECT_NAME")
    if project and docker.is_compose_running(project):
        logger.warning("%sInstance running, you cannot import new instance%s", YELLOW, NC)
        return

    import_dir = Path(archive.stem)
    shutil.unpack_archive(archive)
    shutil.copy(import_dir / "env", ".env")
    propagate_env()
    shutil.copy(import_dir / "docker-compose.yml", docker.DOCKER_DIR)
    db.DATA_DIR.mkdir(exist_ok=True)  # So that Learnagement does not ask for free data
    for sql_file in db.SQL_DIR.iterdir():
        sql_file.unlink()
    shutil.copytree(import_dir / "sql", db.SQL_DIR, dirs_exist_ok=True)
    shutil.rmtree(import_dir)


@cli.command(help="Stop application")
def stop() -> None:
    dotenv.load_dotenv()
    docker.compose_down()


@cli.command()
def gui() -> None:
    """Lance l'interface graphique click-gui-runner pour explorer cette application."""
    try:
        from click_gui_runner.__main__ import main as gui_main
    except ImportError as error:
        raise click.ClickException(
            "click-gui-runner n'est pas installé : il n'est pas publié sur PyPI."
        ) from error
    gui_main(caller=str(Path("Learnagement.py").resolve()))


def handle_signal(_signum: int, _frame: FrameType | None) -> None:
    dotenv.load_dotenv()
    docker.compose_down()
    sys.exit(0)


def main() -> None:
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    cli()
