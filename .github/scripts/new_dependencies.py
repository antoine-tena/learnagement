"""Les dépendances qu'une branche ajoute, manifeste par manifeste, en lignes Markdown.

    python3 .github/scripts/new_dependencies.py <commit de base>

Lit pyproject.toml (dépendances et groupes), package.json et composer.json, au commit de base
(git show) et dans l'arbre de travail ; n'écrit rien quand aucune dépendance n'est ajoutée.
"""

import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

NODE_SECTIONS = ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")
COMPOSER_SECTIONS = ("require", "require-dev")
REQUIREMENT_NAME = re.compile(r"^[A-Za-z0-9._-]+")


def python_names(text: str) -> set[str]:
    """Noms des dépendances d'un pyproject.toml, groupes compris, sans version ni extras."""
    manifest = tomllib.loads(text)
    requirements = list(manifest.get("project", {}).get("dependencies", []))
    for group in manifest.get("dependency-groups", {}).values():
        requirements += [entry for entry in group if isinstance(entry, str)]
    names = (REQUIREMENT_NAME.match(requirement) for requirement in requirements)
    return {match.group(0).lower() for match in names if match}


def section_names(sections: tuple[str, ...]) -> Callable[[str], set[str]]:
    """Lecteur des clés de ces sections d'un manifeste JSON (package.json, composer.json)."""

    def read(text: str) -> set[str]:
        manifest = json.loads(text)
        return {name for section in sections for name in manifest.get(section, {})}

    return read


READERS: dict[str, Callable[[str], set[str]]] = {
    "pyproject.toml": python_names,
    "package.json": section_names(NODE_SECTIONS),
    "composer.json": section_names(COMPOSER_SECTIONS),
}


def tracked_manifests() -> list[Path]:
    listing = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True)
    return [Path(line) for line in listing.stdout.splitlines() if Path(line).name in READERS]


def base_text(base: str, manifest: Path) -> str | None:
    shown = subprocess.run(
        ["git", "show", f"{base}:{manifest.as_posix()}"], capture_output=True, text=True
    )
    return shown.stdout if shown.returncode == 0 else None


def added_names(base: str, manifest: Path) -> set[str]:
    read = READERS[manifest.name]
    head_names = read(manifest.read_text("utf-8"))
    before = base_text(base, manifest)
    return head_names - (read(before) if before is not None else set())


def main(base: str) -> None:
    for manifest in tracked_manifests():
        for name in sorted(added_names(base, manifest)):
            print(f"- `{name}` dans `{manifest.as_posix()}`")


if __name__ == "__main__":
    main(sys.argv[1])
