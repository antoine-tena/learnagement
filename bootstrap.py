#!/usr/bin/env python3
"""
Bootstrap script: lance l'application avec uv, qui prépare l'environnement Python.

Ce script :
1. Vérifie que uv est installé.
2. Crée ou met à jour `.venv` depuis `uv.lock`, sans le modifier.
3. Lance l'application avec les arguments fournis.

Usage:
    python bootstrap.py [args...]
"""
import shutil
import subprocess
import sys

APP_MODULE = "Learnagement"
UV_INSTALL_URL = "https://docs.astral.sh/uv/getting-started/installation/"


def main() -> None:
    uv = shutil.which("uv")
    if uv is None:
        sys.exit(f"!! uv est introuvable, installez-le : {UV_INSTALL_URL}")
    sys.exit(subprocess.call([uv, "run", "--frozen", "python", "-m", APP_MODULE, *sys.argv[1:]]))


if __name__ == "__main__":
    main()
