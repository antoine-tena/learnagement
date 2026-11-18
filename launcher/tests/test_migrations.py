"""Les migrations de `database/migrations/` : MySQL les joue une fois, par ordre alphabétique."""

import re
from collections import Counter
from pathlib import Path

MIGRATION_NAME = re.compile(r"^V(\d+)\.(\d+)\.(\d+)__\w+\.sql$")
SQL_DIR = Path(__file__).resolve().parents[2] / "database" / "migrations"
# Versions partagées avant ce test, déjà jouées sur des bases : leur ordre alphabétique tient.
SHARED_BEFORE_THE_CHECK = {(0, 2, 0)}


def _versions() -> list[tuple[str, tuple[int, int, int]]]:
    migrations = []
    for path in SQL_DIR.glob("*.sql"):
        match = MIGRATION_NAME.match(path.name)
        assert match, f"{path.name} : nom attendu VX.Y.Z__description.sql"
        major, minor, patch = (int(part) for part in match.groups())
        migrations.append((path.name, (major, minor, patch)))
    return migrations


def test_each_new_migration_has_its_own_version() -> None:
    counts = Counter(version for _name, version in _versions())
    shared = {version for version, count in counts.items() if count > 1}
    new_shared = shared - SHARED_BEFORE_THE_CHECK
    assert not new_shared, f"versions en double : {new_shared}"


def test_alphabetical_order_follows_versions() -> None:
    migrations = _versions()
    by_name = [name for name, _version in sorted(migrations)]
    in_version_order = sorted(migrations, key=lambda pair: (pair[1], pair[0]))
    by_version = [name for name, _version in in_version_order]
    assert by_name == by_version
