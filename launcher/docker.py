"""Les commandes docker et compose, lues dans DOCKER_COMMAND et DOCKER_COMPOSE_COMMAND."""

import json
import logging
import os
import shlex
import subprocess
from pathlib import Path

from launcher.config import GREEN, NC

logger = logging.getLogger(__name__)

DOCKER_DIR = Path("docker")
COMPOSE_FILE = DOCKER_DIR / "docker-compose.yml"


def docker_command() -> list[str]:
    return os.environ["DOCKER_COMMAND"].split()


def compose_command() -> list[str]:
    return os.environ["DOCKER_COMPOSE_COMMAND"].split()


def parse_docker_options(options: str | None) -> list[str]:
    """Transforme l'option --docker_option (`-d --build`) en arguments de commande."""
    return shlex.split(options) if options else []


def compose_up(options: list[str]) -> None:
    logger.info("%sRun Docker%s", GREEN, NC)
    # COMPOSE_MENU=false : sans le menu interactif de compose, qui dérègle le terminal
    env = {**os.environ, "COMPOSE_MENU": "false"}
    subprocess.run([*compose_command(), "up", *options], cwd=DOCKER_DIR, env=env, check=True)


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
