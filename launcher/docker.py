"""Les commandes docker et compose, lues dans DOCKER_COMMAND et DOCKER_COMPOSE_COMMAND."""

import json
import logging
import os
import shlex
import shutil
import subprocess
from pathlib import Path

from launcher.config import GREEN, NC, YELLOW

logger = logging.getLogger(__name__)

DOCKER_DIR = Path("docker")
COMPOSE_FILE = DOCKER_DIR / "docker-compose.yml"
COMPOSE_SKELETON = DOCKER_DIR / "docker-compose.yml.skeleton"
COMPOSE_VARIABLES = (
    "INSTANCE_PROTOCOL",
    "INSTANCE_NAME",
    "ENV",
    "PHPMYADMIN_PORT",
    "PHPMYADMIN_DOCKER_PORT",
    "BACKEND_PYTHON_PORT",
    "BACKEND_PYTHON_DOCKER_PORT",
    "FRONT_PHP_PORT",
    "FRONT_PHP_DOCKER_PORT",
    "FRONT_DASH_PORT",
    "FRONT_DASH_DOCKER_PORT",
    "FRONT_NEXTAUTH_PORT",
    "FRONT_NEXTAUTH_DOCKER_PORT",
    "SSL_INTERNAL_DIR",
    "SSL_EXTERNAL_DIR",
    "DOCKER_SSL_INTERNAL_DIR",
    "DOCKER_SSL_EXTERNAL_DIR",
)


def docker_command() -> list[str]:
    return os.environ["DOCKER_COMMAND"].split()


def compose_command() -> list[str]:
    return os.environ["DOCKER_COMPOSE_COMMAND"].split()


def parse_docker_options(options: str | None) -> list[str]:
    """Transforme l'option --docker_option (`-d --build`) en arguments de commande."""
    return shlex.split(options) if options else []


def write_compose_file() -> None:
    """Produit docker-compose.yml depuis son modèle, s'il n'existe pas encore."""
    logger.info("%sDocker configuration%s", GREEN, NC)
    if COMPOSE_FILE.exists():
        if COMPOSE_SKELETON.stat().st_mtime > COMPOSE_FILE.stat().st_mtime:
            logger.warning(
                "%sdocker-compose.yml.skeleton has been updated, "
                "your docker-compose.yml can be deprecated%s",
                YELLOW,
                NC,
            )
        return
    shutil.copy(COMPOSE_SKELETON, COMPOSE_FILE)
    content = COMPOSE_FILE.read_text(encoding="utf-8")
    for name in COMPOSE_VARIABLES:
        content = content.replace(f"${{{name}}}", os.environ[name])
    COMPOSE_FILE.write_text(content, encoding="utf-8")


def compose_up(options: list[str]) -> None:
    logger.info("%sRun Docker%s", GREEN, NC)
    subprocess.run([*compose_command(), "up", *options], cwd=DOCKER_DIR, check=True)


def compose_down() -> None:
    logger.info("%sStop App%s", GREEN, NC)
    subprocess.run([*compose_command(), "down"], cwd=DOCKER_DIR, check=True)
    logger.info("%sApp stopped%s", GREEN, NC)


def is_compose_running(project_name: str) -> bool:
    """Dit si un projet compose tourne ; False si l'outil ne sait pas répondre."""
    try:
        result = subprocess.run(
            [*compose_command(), "ls", "--filter", f"name={project_name}", "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        projects = json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return False
    return any(
        project["Name"] == project_name and project["Status"].startswith("running")
        for project in projects
    )
