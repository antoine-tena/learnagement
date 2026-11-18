"""Génération, chargement et propagation des fichiers .env.

`.env` est l'environnement de l'instance. Il est produit à partir de `deploy/env.skeleton`,
des réponses de l'utilisateur (`.env.default`) et des autres parts `.env.<part>` (`.env.git` :
le commit), puis des valeurs de l'environnement choisi (`.env_<env>.env`, copié de
`deploy/env.<env>`). Une part ne redéfinit jamais une clé d'une autre.
"""

import logging
import re
import shutil
import sys
from pathlib import Path

import dotenv

from launcher.config import COMPOSE_DIR, CONTAINER_APP_DIRS, CONTAINERS, GREEN, NC, RED, YELLOW
from launcher.tools import ask, generate_secret, get_local_ip_and_hostname

logger = logging.getLogger(__name__)

type EnvVars = dict[str, str]

ENV_FILE = Path(".env")
DEFAULT_PART = Path(".env.default")
PART_PATTERN = re.compile(r"^\.env\.([a-z]+)$")


def env_file_of(env: str) -> Path:
    return Path(f".env_{env}.env")


def load_env_file(filepath: str | Path) -> EnvVars:
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


def save_env_file(env_vars: EnvVars, filepath: str | Path) -> None:
    """Écrit un fichier .env, avec des guillemets autour des valeurs qui ont des espaces."""
    lines = [
        f'{key}="{value}"' if " " in value else f"{key}={value}" for key, value in env_vars.items()
    ]
    Path(filepath).write_text("\n".join(lines) + "\n", encoding="utf-8")


def apply_env_file(env_vars: EnvVars, filepath: str | Path) -> EnvVars:
    """Met à jour les clés déjà présentes avec les valeurs d'un fichier env."""
    file_vars = load_env_file(filepath)
    return {key: file_vars.get(key, value) for key, value in env_vars.items()}


def load_env_parts(directory: Path = Path(".")) -> EnvVars:
    """L'union des parts `.env.<part>` ; une clé définie deux fois est une erreur."""
    env_vars: EnvVars = {}
    for path in sorted(directory.iterdir()):
        if not PART_PATTERN.match(path.name) or not path.is_file():
            continue
        for key, value in load_env_file(path).items():
            if key in env_vars:
                raise ValueError(f"La clé '{key}' de '{path.name}' est déjà définie ailleurs.")
            env_vars[key] = value
    return env_vars


def generate_base_env() -> EnvVars:
    """Demande le nom et les mots de passe de l'instance, et génère ses secrets."""
    env_vars = load_env_file("deploy/env.skeleton")

    instance_name = ask("Give the intance name (lowercase): ").lower()
    env_vars["INSTANCE_NAME"] = instance_name
    env_vars["COMPOSE_PROJECT_NAME"] = f"learnagement_{instance_name}"

    env_vars["CAS_SERVICE_TOKEN"] = generate_secret("CAS Generated Encryption Key").hex()
    env_vars["JWT_SIGNING_KEY"] = generate_secret("LNM Generated Encryption Key").hex()
    env_vars["NEXTAUTH_SECRET"] = generate_secret("NextAuth.js Generated Encryption Key").hex()
    protocol = "http"
    env_vars["FRONT_PHP_PROTOCOL"] = protocol

    env_vars["INSTANCE_PROTOCOL"] = protocol
    env_vars["INSTANCE_IP"], env_vars["INSTANCE_URL"] = get_local_ip_and_hostname()

    env_vars["MYSQL_SERVER"] = f"learnagement_data_mysql_{instance_name}"
    env_vars["MYSQL_ROOT_PASSWORD"] = ask("MySQL Root password: ", is_secret=True)
    env_vars["MYSQL_USER_PASSWORD"] = ask("Give the MySQL User password: ", is_secret=True)
    env_vars["LEARNAGEMENT_ADMINISTRATOR_PASSWORD"] = ask(
        "Give the Learnagement Administrator password: ", is_secret=True
    )

    env_vars["BACKEND_PYTHON_DOCKER_URL"] = f"learnagement_backend_python_{instance_name}"
    return env_vars


def _copy_env_templates() -> None:
    for name in ("dev", "prod"):
        if not env_file_of(name).exists():
            shutil.copy(f"deploy/env.{name}", env_file_of(name))


def _env_dirs() -> list[Path]:
    """Les dossiers qui reçoivent une copie de .env, pour l'environnement en cours."""
    env = dotenv.dotenv_values(ENV_FILE).get("ENV") or "dev"
    app_dirs = (CONTAINER_APP_DIRS[container] for container in CONTAINERS[env])
    return [Path(COMPOSE_DIR), *(Path(app_dir) for app_dir in app_dirs if app_dir)]


def propagate_env() -> None:
    """Recopie .env dans le dossier de chaque conteneur."""
    for directory in _env_dirs():
        shutil.copy(ENV_FILE, directory / ".env")
        logger.info("%sCopied: .env -> %s%s", GREEN, directory / ".env", NC)


def remove_env_files() -> None:
    """Supprime .env, ses copies et les environnements, pour en générer de nouveaux."""
    if ENV_FILE.exists():
        for directory in _env_dirs():
            (directory / ".env").unlink(missing_ok=True)
    for path in (ENV_FILE, DEFAULT_PART, env_file_of("dev"), env_file_of("prod")):
        path.unlink(missing_ok=True)


def load_env(env: str | None = None) -> None:
    """Génère .env s'il manque (en demandant l'environnement), le propage et le charge."""
    if not ENV_FILE.exists():
        if not env:
            print(f"{YELLOW}env file doesn't exist and environment not specified.{NC}")
            env = ask("Give the required environment (alpha lowercase): ").lower()
        _copy_env_templates()
        save_env_file(generate_base_env(), DEFAULT_PART)
        if not env_file_of(env).exists():
            logger.error("%sSpecific env file '%s' doesn't exist%s", RED, env_file_of(env), NC)
            sys.exit(1)
        save_env_file(apply_env_file(load_env_parts(), env_file_of(env)), ENV_FILE)
    propagate_env()
    dotenv.load_dotenv(ENV_FILE)
