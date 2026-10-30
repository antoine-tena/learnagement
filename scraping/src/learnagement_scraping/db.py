"""Écritures en base : toujours des requêtes paramétrées, et une erreur n'est jamais avalée."""

import os
from collections.abc import Iterable, Sequence
from typing import Protocol

import mysql.connector

type Row = Sequence[str | int | float | None]

HOURS_COLUMNS = {"Nb heures Cours": "hCM", "Nb heures TD": "hTD", "Nb heures TP": "hTP"}


class Cursor(Protocol):
    def executemany(self, operation: str, seq_params: Sequence[Row]) -> object: ...

    def close(self) -> object: ...


class Connection(Protocol):
    def cursor(self) -> Cursor: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def close(self) -> None: ...


def connect() -> Connection:
    """Se connecte avec les mêmes variables d'environnement que l'API."""
    connection: Connection = mysql.connector.connect(
        user=os.environ["MYSQL_USER_LOGIN"],
        password=os.environ["MYSQL_USER_PASSWORD"],
        host=os.environ["MYSQL_SERVER"],
        port=int(os.environ["MYSQL_PORT"]),
        database=os.environ["MYSQL_DB"],
    )
    return connection


def write_rows(connection: Connection, query: str, rows: Iterable[Row]) -> int:
    """Écrit toutes les lignes dans une même transaction et renvoie leur nombre."""
    values = list(rows)
    cursor = connection.cursor()
    try:
        cursor.executemany(query, values)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
    return len(values)


def save_disciplines(connection: Connection, names: Iterable[str]) -> int:
    return write_rows(
        connection,
        "INSERT INTO MAQUETTE_discipline (nom) VALUES (%s)",
        [(name,) for name in names],
    )


def save_semesters(connection: Connection, labels: Iterable[str]) -> int:
    """Enregistre chaque semestre avec le numéro lu dans son libellé (`S5` donne 5)."""
    rows = []
    for label in labels:
        digits = "".join(character for character in label if character.isdigit())
        if not digits:
            raise ValueError(f"Semestre sans numéro : {label!r}")
        rows.append((int(digits), label))
    return write_rows(
        connection,
        "INSERT INTO LNM_semestre (id_semestre, semestre) VALUES (%s, %s)",
        rows,
    )


def save_teachers(connection: Connection, rows: Iterable[tuple[str, str, str]]) -> int:
    """Crée les enseignants (prénom, nom, mail), avec un service et une décharge à compléter."""
    return write_rows(
        connection,
        "INSERT INTO LNM_enseignant "
        "(prenom, nom, mail, `service statutaire`, decharge) VALUES (%s, %s, %s, 0, 0)",
        rows,
    )


def save_module_hours(connection: Connection, code: str, details: dict[str, str]) -> int:
    """Met à jour les volumes horaires présents dans la fiche d'un module."""
    written = 0
    for label, column in HOURS_COLUMNS.items():
        if label in details:
            written += write_rows(
                connection,
                f"UPDATE MAQUETTE_module SET {column} = %s WHERE code_module = %s",
                [(float(details[label].replace(",", ".")), code)],
            )
    return written
