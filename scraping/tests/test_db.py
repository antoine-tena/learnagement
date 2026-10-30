"""Les écritures, sur une fausse connexion : aucune base."""

from collections.abc import Sequence
from dataclasses import dataclass, field

import pytest

from learnagement_scraping import db


@dataclass
class FakeConnection:
    fail: bool = False
    executed: list[tuple[str, list[db.Row]]] = field(default_factory=list)
    commits: int = 0
    rollbacks: int = 0

    def cursor(self) -> FakeConnection:
        return self

    def executemany(self, operation: str, seq_params: Sequence[db.Row]) -> None:
        if self.fail:
            raise RuntimeError("base indisponible")
        self.executed.append((operation, list(seq_params)))

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def close(self) -> None:
        return None


def test_disciplines_are_passed_as_parameters() -> None:
    connection = FakeConnection()
    assert db.save_disciplines(connection, ["L'info"]) == 1
    query, rows = connection.executed[0]
    assert "L'info" not in query
    assert rows == [("L'info",)]
    assert connection.commits == 1


def test_semesters_take_their_number_from_the_label() -> None:
    connection = FakeConnection()
    db.save_semesters(connection, ["S5"])
    assert connection.executed[0][1] == [(5, "S5")]


def test_semester_without_number_is_refused() -> None:
    with pytest.raises(ValueError, match="sans numéro"):
        db.save_semesters(FakeConnection(), ["Aucun"])


def test_teachers_fill_the_required_columns() -> None:
    connection = FakeConnection()
    db.save_teachers(connection, [("Alice", "DUPONT", "alice@example.org")])
    query, rows = connection.executed[0]
    assert "LNM_enseignant " in query
    assert "`service statutaire`" in query
    assert rows == [("Alice", "DUPONT", "alice@example.org")]


def test_module_hours_only_update_known_fields() -> None:
    connection = FakeConnection()
    written = db.save_module_hours(
        connection,
        "INFO731",
        {"Nb heures TD": "12,5", "Semestre": "S7"},
    )
    assert written == 1
    query, rows = connection.executed[0]
    assert "hTD = %s" in query
    assert rows == [(12.5, "INFO731")]


def test_failure_rolls_back_and_is_raised() -> None:
    connection = FakeConnection(fail=True)
    with pytest.raises(RuntimeError):
        db.save_disciplines(connection, ["Info"])
    assert connection.rollbacks == 1
    assert connection.commits == 0
