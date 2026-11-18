"""Les commandes du lanceur : `python Learnagement.py <commande>`."""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path
from types import FrameType

import click
import dotenv
from click_default_group import DefaultGroup

from launcher import compose, db, docker, instance
from launcher.config import CONTAINERS, GREEN, NC, RED, YELLOW, envs
from launcher.env import load_env
from launcher.git import get_branch
from launcher.tools import protect_tty

logging.basicConfig(
    format=f"{RED}Learnagement [%(filename)s:%(lineno)d] |{NC}  "
    "%(asctime)s,%(msecs)03d - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

ENV_CHOICES = click.Choice(sorted(envs))
ENV_HELP = "Environment to use: " + ", ".join(sorted(envs))


def _security_check() -> None:
    branch = get_branch()
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


async def _setup_administrator() -> None:
    """Ajoute l'administrateur dès que la base répond, puis attend tous les conteneurs."""
    await db.wait_for_mysql_healthy()
    await db.create_administrator_with_retry()
    await compose.wait_for_all_ready()
    web_url = f"{os.environ['INSTANCE_PROTOCOL']}://{os.environ['INSTANCE_URL']}"
    logger.info("%sWeb Apps runs on: %s:%s%s", GREEN, web_url, os.environ["FRONT_PHP_PORT"], NC)
    logger.info(
        "%sPHPMyAdmin runs on: http://127.0.0.1:%s%s", GREEN, os.environ["PHPMYADMIN_PORT"], NC
    )
    logger.info("%sAdmin is deactivated by default%s", GREEN, NC)


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
    if instance.is_running():
        logger.warning("%sInstance already running%s", YELLOW, NC)
        return

    load_env()
    db.prepare_init_files()
    db.prepare_initial_data()
    compose.write_compose_file(CONTAINERS[os.environ["ENV"]])
    _security_check()
    try:
        asyncio.run(_run_instance(options))
    finally:
        docker.compose_down()


@click.group(cls=DefaultGroup, default="start", default_if_no_args=True)
def cli() -> None:
    pass


@cli.command(help="Generate environment without starting the application")
@click.option("--env", type=ENV_CHOICES, default="dev", help=ENV_HELP)
def generate_env(env: str) -> None:
    load_env(env)


@cli.command(help="Start the application")
@click.option("--docker_option", default=None, help="See podman compose options")
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
        instance.reset()

    if env:
        instance.switch_env(env)
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
    instance.export()


@cli.command(help="Import an instance from a zip archive")
@click.option("--file", "archive", required=True, type=click.Path(exists=True, path_type=Path))
def import_instance(archive: Path) -> None:
    dotenv.load_dotenv()
    instance.import_archive(archive)


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
    """Interrompt le lancement : l'arrêt des conteneurs se fait dans `_start`."""
    raise KeyboardInterrupt


def main() -> None:
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    protect_tty()
    cli()
