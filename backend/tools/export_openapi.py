"""Exporte le schéma OpenAPI de l'API dans un fichier versionné, ou vérifie qu'il est à jour.

    uv run python -m tools.export_openapi --output ../openapi.json           # l'écrire
    uv run python -m tools.export_openapi --output ../openapi.json --check   # le vérifier (CI)

Le schéma se calcule sans base ni service : les variables factices des tests suffisent à
importer l'application.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import tests.conftest  # noqa: F401  (pose les variables factices avant l'import de l'app)

EXIT_DRIFT = 1


def render_schema() -> str:
    """Le schéma OpenAPI de l'application, en JSON stable (clés triées, fin de ligne)."""
    logging.disable(logging.INFO)  # les routes générées se journalisent à l'import
    from app import app

    return json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, required=True, help="Fichier du schéma")
    parser.add_argument("--check", action="store_true", help="Échoue si le fichier diffère du code")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    arguments = parse_arguments(argv)
    schema = render_schema()
    if not arguments.check:
        arguments.output.write_text(schema, encoding="utf-8")
        return 0
    is_current = arguments.output.exists() and arguments.output.read_text("utf-8") == schema
    if not is_current:
        print(
            f"{arguments.output} ne correspond plus au code : "
            "uv run python -m tools.export_openapi --output ../openapi.json",
            file=sys.stderr,
        )
        return EXIT_DRIFT
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
