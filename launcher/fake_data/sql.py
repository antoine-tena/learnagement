"""L'écriture des valeurs et des requêtes SQL du jeu fictif."""

from collections.abc import Sequence
from datetime import date, datetime

type SqlValue = str | int | float | date | datetime | Raw | None


class Raw(str):
    """Une expression SQL écrite telle quelle (sous-requête, fonction)."""

    __slots__ = ()


def literal(value: SqlValue) -> str:
    """La valeur écrite en SQL MySQL."""
    match value:
        case None:
            return "NULL"
        case Raw():
            return str(value)
        case bool():
            return str(int(value))
        case int() | float():
            return str(value)
        case datetime():
            return f"'{value:%Y-%m-%d %H:%M:%S}'"
        case date():
            return f"'{value.isoformat()}'"
        case str():
            escaped = value.replace("\\", "\\\\").replace("'", "\\'")
            return f"'{escaped}'"


def insert(table: str, columns: Sequence[str], rows: Sequence[Sequence[SqlValue]]) -> str:
    """Un `INSERT` de plusieurs lignes ; aucun texte quand il n'y a pas de ligne."""
    if not rows:
        return ""
    names = ", ".join(f"`{column}`" for column in columns)
    values = ",\n  ".join("(" + ", ".join(literal(v) for v in row) + ")" for row in rows)
    return f"INSERT INTO `{table}` ({names}) VALUES\n  {values};\n"
