"""Le fichier compose.yaml de l'instance, assemblé depuis `docker/compose/`, et son état."""

import asyncio
import json
import logging
import os
from pathlib import Path

from launcher.config import GREEN, NC
from launcher.docker import COMPOSE_FILE, DOCKER_DIR, compose_command, docker_command

logger = logging.getLogger(__name__)

FRAGMENTS_DIR = DOCKER_DIR / "compose"
# Les variables remplacées dans le fichier ; les autres (mots de passe) sont lues par compose
# dans docker/.env au lancement, pour ne pas les écrire en clair.
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
    "FRONT_PHP_PROTOCOL",
    "FRONT_DASH_PORT",
    "FRONT_DASH_DOCKER_PORT",
    "FRONT_NEXTAUTH_PORT",
    "FRONT_NEXTAUTH_DOCKER_PORT",
    "SSL_INTERNAL_DIR",
    "SSL_EXTERNAL_DIR",
    "DOCKER_SSL_INTERNAL_DIR",
    "DOCKER_SSL_EXTERNAL_DIR",
    "USERNS_MODE",
)
# Sous podman sans root, keep-id fait de l'utilisateur de la machine celui du conteneur : un
# conteneur non root écrit alors dans le code monté (node_modules du front). docker : host.
USERNS_MODE_PODMAN = "keep-id"
USERNS_MODE_DOCKER = "host"
# Le premier démarrage installe les dépendances : les sondes s'accordent environ 5 minutes.
READY_TIMEOUT_SECONDS = 300


def render_compose(containers: list[str], variables: dict[str, str]) -> str:
    """Le contenu de compose.yaml pour ces conteneurs."""
    names = ["_head", *containers, "_tail"]
    content = "".join((FRAGMENTS_DIR / f"{name}.yml").read_text(encoding="utf-8") for name in names)
    for name in COMPOSE_VARIABLES:
        content = content.replace(f"${{{name}}}", variables[name])
    return content


def userns_mode(docker_executable: str) -> str:
    """Le mode d'espace de noms des utilisateurs selon l'outil : podman ou docker."""
    is_podman = Path(docker_executable).name == "podman"
    return USERNS_MODE_PODMAN if is_podman else USERNS_MODE_DOCKER


def write_compose_file(containers: list[str]) -> None:
    """Écrit compose.yaml, à chaque lancement, pour les conteneurs de l'environnement."""
    logger.info("%sDocker configuration%s", GREEN, NC)
    variables = {**os.environ, "USERNS_MODE": userns_mode(docker_command()[0])}
    COMPOSE_FILE.write_text(render_compose(containers, variables), encoding="utf-8")


def _is_ready(container: dict[str, object]) -> bool:
    """Un conteneur lancé et en bonne santé, ou un conteneur ponctuel terminé sans erreur."""
    if container.get("State") == "exited":
        return container.get("ExitCode") == 0
    return container.get("State") == "running" and container.get("Health", "") in ("", "healthy")


def parse_compose_ps(output: str) -> list[dict[str, object]]:
    """Les conteneurs de `compose ps --format json` : une liste, ou un objet par ligne."""
    containers: list[dict[str, object]] = []
    for line in output.splitlines():
        if line.strip():
            parsed = json.loads(line)
            containers.extend(parsed if isinstance(parsed, list) else [parsed])
    return containers


async def wait_for_all_ready(timeout: int = READY_TIMEOUT_SECONDS, poll_interval: int = 3) -> None:
    """Attend que tous les conteneurs du projet soient prêts."""
    command = [
        *compose_command(),
        *("-p", os.environ["COMPOSE_PROJECT_NAME"], "ps", "--all", "--format", "json"),
    ]
    elapsed = 0
    while elapsed < timeout:
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        containers = parse_compose_ps(stdout.decode())
        if containers and all(_is_ready(container) for container in containers):
            return
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(f"Tous les conteneurs ne sont pas prêts après {timeout}s")
