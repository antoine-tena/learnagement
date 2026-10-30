"""Génération et propagation des fichiers .env."""

import logging
import shutil
from getpass import getpass
from pathlib import Path

from launcher.config import (
    GREEN,
    NC,
    containers_dev,
    containers_prod,
    containers_system,
)
from launcher.tools import generate_secret, get_local_ip_and_hostname

logger = logging.getLogger(__name__)

type EnvVars = dict[str, str]


def load_env_file(filepath: str) -> EnvVars:
    """Lit un fichier env, sans ses lignes vides, ses commentaires et ses guillemets."""
    env_vars: EnvVars = {}
    for raw_line in Path(filepath).read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            value = value[1:-1]
        env_vars[key.strip()] = value
    return env_vars


def save_env_file(env_vars: EnvVars, filepath: str) -> None:
    """Écrit un fichier .env, avec des guillemets autour des valeurs qui ont des espaces."""
    lines = [
        f'{key}="{value}"' if " " in value else f"{key}={value}" for key, value in env_vars.items()
    ]
    Path(filepath).write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply_env_file(env_vars: EnvVars, filepath: str) -> EnvVars:
    """Met à jour les clés déjà présentes avec les valeurs d'un fichier env."""
    file_vars = load_env_file(filepath)
    return {key: file_vars.get(key, value) for key, value in env_vars.items()}


def generate_base_env() -> EnvVars:
    """Demande le nom et les mots de passe de l'instance, et génère ses secrets."""
    env_vars = load_env_file("config/env.skeleton")

    instance_name = input("Give the intance name (lowercase): ").lower()
    env_vars["INSTANCE_NAME"] = instance_name
    env_vars["COMPOSE_PROJECT_NAME"] = f"learnagement_{instance_name}"

    env_vars["CAS_SERVICE_TOKEN"] = generate_secret("CAS Generated Encryption Key").hex()
    env_vars["JWT_SIGNING_KEY"] = generate_secret("LNM Generated Encryption Key").hex()
    env_vars["NEXTAUTH_SECRET"] = generate_secret("NextAuth.js Generated Encryption Key").hex()
    protocol = "http"
    env_vars["FRONT_PHP_PROTOCOL"] = protocol

    env_vars["INSTANCE_PROTOCOL"] = protocol
    env_vars["INSTANCE_IP"], env_vars["INSTANCE_URL"] = get_local_ip_and_hostname()

    env_vars["MYSQL_SERVER"] = f"learnagement_mysql_{instance_name}"
    env_vars["MYSQL_ROOT_PASSWORD"] = getpass("Give the MySQL Root password: ")
    env_vars["MYSQL_USER_PASSWORD"] = getpass("Give the MySQL User password: ")
    env_vars["LEARNAGEMENT_ADMINISTRATOR_PASSWORD"] = getpass(
        "Give the Learnagement Administrator password: "
    )

    env_vars["BACKEND_PYTHON_DOCKER_URL"] = f"learnagement_backend_python_{instance_name}"

    return env_vars


def propagate_env() -> None:
    """Recopie .env dans le dossier de chaque conteneur."""
    for container in containers_system + containers_dev + containers_prod:
        target = Path(container) / ".env"
        shutil.copy(".env", target)
        logger.info("%sCopied: .env -> %s%s", GREEN, target, NC)
