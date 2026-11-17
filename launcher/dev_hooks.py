"""Les hooks de pré-commit du poste de développement : règles et mise en forme avant chaque commit.

Appelé par `bootstrap.py`, sans dépendance hors de la bibliothèque standard : l'environnement
Python du lanceur n'existe pas encore. Jamais sur une instance de production (`ENV=prod`).
"""

import shutil
import subprocess
from pathlib import Path

ENV_FILE = Path(".env")
PRODUCTION_ENV = "prod"
# L'outil et le paquet qui le fournit : `charter` vient d'ion-repo, qui tient les règles du repo.
TOOLS = {"pre-commit": "pre-commit", "charter": "ion-repo"}


def is_production(env_file: Path = ENV_FILE) -> bool:
    if not env_file.exists():
        return False
    for line in env_file.read_text(encoding="utf-8").splitlines():
        key, _, value = line.partition("=")
        if key.strip() == "ENV":
            return value.strip().strip("\"'") == PRODUCTION_ENV
    return False


def missing_packages() -> list[str]:
    return [package for tool, package in TOOLS.items() if shutil.which(tool) is None]


def install_dev_hooks(uv: str) -> str:
    """Installe les outils qui manquent et le hook ; renvoie ce qui a été fait, pour l'afficher."""
    if is_production():
        return "instance de production, hooks de pré-commit non installés"
    for package in missing_packages():
        if subprocess.call([uv, "tool", "install", package]) != 0:
            return f"{package} non installé, hooks de pré-commit non installés"
    pre_commit = shutil.which("pre-commit")
    if pre_commit is None:
        return "pre-commit introuvable dans le PATH (uv tool update-shell), hooks non installés"
    if subprocess.call([pre_commit, "install"], stdout=subprocess.DEVNULL) != 0:
        return "pre-commit install a échoué"
    return "hooks de pré-commit installés"
