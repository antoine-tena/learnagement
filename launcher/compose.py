"""Le fichier compose.yaml de l'instance, assemblé depuis les fragments, et son état."""

import asyncio
import json
import logging
import os
import re
from pathlib import Path

from launcher.config import COMPOSE_FRAGMENTS, GREEN, NC
from launcher.docker import COMPOSE_FILE, DOCKER_DIR, compose_command, docker_command

logger = logging.getLogger(__name__)

FRAGMENTS_DIR = DOCKER_DIR / "compose"
# Les variables remplacées dans le fichier ; les autres (mots de passe) sont lues par compose
# dans deploy/.env au lancement, pour ne pas les écrire en clair.
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
# podman ps n'a pas de clé Health : la santé est à la fin de Status, « Up 3 minutes (healthy) »
HEALTH_IN_STATUS = re.compile(r"\((healthy|unhealthy|starting)\)")


def render_compose(containers: list[str], variables: dict[str, str]) -> str:
    """Le contenu de compose.yaml pour ces conteneurs."""
    fragments = [
        FRAGMENTS_DIR / "_head.yml",
        *(Path(COMPOSE_FRAGMENTS[container]) for container in containers),
        FRAGMENTS_DIR / "_tail.yml",
    ]
    content = "".join(fragment.read_text(encoding="utf-8") for fragment in fragments)
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


def container_health(container: dict[str, object]) -> str:
    """La santé : clé Health, ou à défaut entre parenthèses dans Status (podman)."""
    health = container.get("Health")
    if health:
        return str(health)
    match = HEALTH_IN_STATUS.search(str(container.get("Status", "")))
    return match.group(1) if match else ""


def _is_ready(container: dict[str, object]) -> bool:
    """Un conteneur lancé et en bonne santé, ou un conteneur ponctuel terminé sans erreur."""
    if container.get("State") == "exited":
        return container.get("ExitCode") == 0
    return container.get("State") == "running" and container_health(container) in ("", "healthy")


def parse_compose_ps(output: str) -> list[dict[str, object]]:
    """Les conteneurs de `compose ps --format json` : un tableau (podman), ou un objet par ligne."""
    try:
        parsed = json.loads(output) if output.strip() else []
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        return [json.loads(line) for line in output.splitlines() if line.strip()]


def compose_ps_command(is_podman: bool) -> list[str]:
    """`compose ps` en JSON, arrêtés compris : podman-compose les liste sans --all, qu'il refuse."""
    all_flag = [] if is_podman else ["--all"]
    project = os.environ["COMPOSE_PROJECT_NAME"]
    return [*compose_command(), "-p", project, "ps", *all_flag, "--format", "json"]


async def wait_for_all_ready(timeout: int = READY_TIMEOUT_SECONDS, poll_interval: int = 3) -> None:
    """Attend que tous les conteneurs du projet soient prêts."""
    command = compose_ps_command(userns_mode(docker_command()[0]) == USERNS_MODE_PODMAN)
    elapsed = 0
    while elapsed < timeout:
        # podman-compose ne trouve le projet qu'à côté de son compose.yaml
        process = await asyncio.create_subprocess_exec(
            *command, cwd=DOCKER_DIR, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        containers = parse_compose_ps(stdout.decode())
        if containers and all(_is_ready(container) for container in containers):
            return
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
    raise TimeoutError(f"Tous les conteneurs ne sont pas prêts après {timeout}s")
