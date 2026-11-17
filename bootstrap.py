#!/usr/bin/env python3
"""
Bootstrap script: lance l'application avec uv, qui prépare l'environnement Python.

Ce script :
1. Vérifie que uv est installé.
2. Installe les hooks git qui tiennent `.env.git` (le commit de l'instance) à jour, et ceux de
   pré-commit (règles et mise en forme), sauf en production.
3. Crée ou met à jour `.venv` depuis `uv.lock`, sans le modifier.
4. Lance l'application avec les arguments fournis.

Usage:
    python bootstrap.py [args...]
"""

import shutil
import subprocess
import sys

from launcher.dev_hooks import install_dev_hooks
from launcher.git import install_hooks, write_commit_file

APP_MODULE = "Learnagement"
UV_INSTALL_URL = "https://docs.astral.sh/uv/getting-started/installation/"


def configure_git() -> None:
    """Installe les hooks git du commit, puis écrit le commit courant."""
    written = install_hooks(repo_dir=".", is_short=True)
    if written:
        print(f">> Hooks Git installés ({len(written)}) : {', '.join(h.name for h in written)}")
    else:
        print("!! Pas de dépôt Git détecté, hooks non installés.")
    commit = write_commit_file(is_short=True)
    print(f">> Commit courant : {commit}" if commit else "!! Impossible de lire le commit.")


def main() -> None:
    uv = shutil.which("uv")
    if uv is None:
        sys.exit(f"!! uv est introuvable, installez-le : {UV_INSTALL_URL}")
    configure_git()
    print(f">> {install_dev_hooks(uv)}")
    sys.exit(subprocess.call([uv, "run", "--frozen", "python", "-m", APP_MODULE, *sys.argv[1:]]))


if __name__ == "__main__":
    main()
