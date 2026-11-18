"""Intitulés des modules : aucune trace d'un rechercher-remplacer dans les données."""

from pathlib import Path

DB_DIR = Path(__file__).resolve().parents[2] / "database"
DAMAGED_TITLE = "Analyse et front_DashPlotly de données"
FIXED_TITLE = "Analyse et visualisation de données"


def test_free_data_has_no_damaged_module_title() -> None:
    damaged_files = [
        path.name
        for path in (DB_DIR / "open-data").rglob("*.sql")
        if DAMAGED_TITLE in path.read_text(encoding="utf-8")
    ]
    assert damaged_files == []


def test_a_migration_fixes_existing_databases() -> None:
    migrations = [
        path.read_text(encoding="utf-8") for path in (DB_DIR / "migrations").glob("V*.sql")
    ]
    assert any(DAMAGED_TITLE in text and FIXED_TITLE in text for text in migrations)
