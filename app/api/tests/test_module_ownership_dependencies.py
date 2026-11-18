import re
import sqlite3
from collections.abc import Callable, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

from access_control.checker import check_access
from api.dependencies import Rows, get_current_active_user
from domains import maquette_module
from models.request import SQLRequest
from models.user import User

SCHEMA = """
CREATE TABLE MAQUETTE_module (
    id_module INTEGER PRIMARY KEY, id_responsable INTEGER);
CREATE TABLE MAQUETTE_module_sequencage (
    id_module_sequencage INTEGER PRIMARY KEY, id_module INTEGER,
    id_intervenant_principal INTEGER);
CREATE TABLE MAQUETTE_module_sequence (
    id_module_sequence INTEGER PRIMARY KEY, id_module_sequencage INTEGER,
    id_intervenant_principal INTEGER);
CREATE TABLE CLASS_session (
    id_session INTEGER PRIMARY KEY, id_module_sequence INTEGER,
    id_enseignant INTEGER);

INSERT INTO MAQUETTE_module VALUES (1, 1), (2, 2);
INSERT INTO MAQUETTE_module_sequencage VALUES (10, 1, NULL), (20, 2, NULL);
INSERT INTO MAQUETTE_module_sequence   VALUES (100, 10, NULL), (200, 20, NULL);
INSERT INTO CLASS_session              VALUES (1000, 100, NULL), (2000, 200, 2);
"""

DEPS_SCHEMA = """
CREATE TABLE MAQUETTE_dependance_sequence (
    id_sequence_prev INTEGER, id_sequence_next INTEGER,
    PRIMARY KEY (id_sequence_prev, id_sequence_next));

INSERT INTO MAQUETTE_module_sequencage VALUES (11, 1, NULL), (21, 2, NULL);
INSERT INTO MAQUETTE_module_sequence   VALUES (101, 11, NULL), (201, 21, NULL);
INSERT INTO MAQUETTE_dependance_sequence VALUES (100, 101), (200, 201), (101, 200);
"""

type CallAs = Callable[..., Response]


def make_user(id_: int, role: str, name: str) -> User:
    return User(
        id=id_,
        prenom=name,
        nom=name,
        ExplicitSecondaryK=name,
        main_role=role,
        roles=["connected_user", role, name],
    )


TEACHER_1 = make_user(1, "enseignant", "Alice Responsable1")
TEACHER_2 = make_user(2, "enseignant", "Bernard Responsable2")
STUDENT_1 = make_user(1, "etudiant", "Etienne Etudiant")


@pytest.fixture
def db(monkeypatch: pytest.MonkeyPatch) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)

    def fake_db_request(requester: User, request: SQLRequest) -> Rows:
        check_access(request=request, user=requester)
        sql = re.sub(r"%\((\w+)\)s", r":\1", request.request)
        cur = conn.execute(sql, request.params or {})
        rows = [dict(r) for r in cur.fetchall()] if cur.description else []
        conn.commit()
        return rows

    monkeypatch.setattr(maquette_module, "db_request", fake_db_request)
    monkeypatch.setattr("api.dependencies.db_request", fake_db_request)
    yield conn
    conn.close()


@pytest.fixture
def db_deps(db: sqlite3.Connection) -> sqlite3.Connection:
    db.executescript(DEPS_SCHEMA)
    return db


@pytest.fixture
def call_as(db: sqlite3.Connection) -> CallAs:
    app = FastAPI()
    app.include_router(maquette_module.router)
    client = TestClient(app, raise_server_exceptions=False)

    def _call(user: User, method: str, url: str, **kwargs: object) -> Response:
        app.dependency_overrides[get_current_active_user] = lambda: user
        return client.request(method, url, **kwargs)

    return _call


def scalar(db: sqlite3.Connection, sql: str) -> int | None:
    row = db.execute(sql).fetchone()
    return None if row is None else row[0]


def dep_count(
    db: sqlite3.Connection, prev: int | None = None, nxt: int | None = None
) -> int | None:
    sql = "SELECT COUNT(*) FROM MAQUETTE_dependance_sequence"
    if prev is not None:
        sql += f" WHERE id_sequence_prev={prev} AND id_sequence_next={nxt}"
    return scalar(db, sql)


# ─────────────────────────────────────────────
# POST /modules/{id_module}/dependencies/
# ─────────────────────────────────────────────

# (utilisateur, module dans l'URL, (prev, next), autorisé)
# Les paires sont absentes du jeu initial (la PK ferait échouer l'INSERT).
# (101, 100) est l'inverse de (100, 101) : l'API ne détecte pas les cycles,
# on s'en sert ici uniquement pour obtenir une paire interne libre.
ADD_MATRIX = [
    pytest.param(TEACHER_1, 1, (101, 100), True, id="T1-url1-interne-legitime"),
    pytest.param(TEACHER_2, 2, (201, 200), True, id="T2-url2-interne-legitime"),
    pytest.param(TEACHER_1, 1, (100, 200), True, id="T1-url1-croise-une-extremite-a-lui"),
    # URL de son module, mais aucune des deux séquences ne lui appartient : la faille
    pytest.param(TEACHER_1, 1, (201, 200), False, id="T1-url1-sequences-etrangeres"),
    pytest.param(TEACHER_2, 2, (101, 100), False, id="T2-url2-sequences-etrangeres"),
    # URL du module de l'autre : il n'en est pas responsable
    pytest.param(TEACHER_1, 2, (201, 200), False, id="T1-url2-module-etranger"),
    pytest.param(TEACHER_2, 1, (101, 100), False, id="T2-url1-module-etranger"),
]


@pytest.mark.parametrize("user, url_module, pair, allowed", ADD_MATRIX)
def test_add_dependency_ownership(
    call_as: CallAs,
    db_deps: sqlite3.Connection,
    user: User,
    url_module: int,
    pair: tuple[int, int],
    allowed: bool,
) -> None:
    prev, nxt = pair
    total_before = dep_count(db_deps)

    call_as(
        user,
        "POST",
        f"/modules/{url_module}/dependencies",
        json={"id_sequence_prev": prev, "id_sequence_next": nxt},
    )

    if allowed:
        assert dep_count(db_deps, prev, nxt) == 1, (
            "Le responsable légitime n'a pas pu créer la dépendance"
        )
    else:
        assert dep_count(db_deps, prev, nxt) == 0, (
            f"{user.prenom} (module {url_module} dans l'URL) a créé la dépendance {pair} "
            f"entre des séquences qui ne lui appartiennent pas"
        )
        assert dep_count(db_deps) == total_before


# ─────────────────────────────────────────────
# DELETE /modules/{id_module}/dependencies/{prev}/{next}
# ─────────────────────────────────────────────

DELETE_MATRIX = [
    pytest.param(TEACHER_1, 1, (100, 101), True, id="T1-url1-interne-legitime"),
    pytest.param(TEACHER_2, 2, (200, 201), True, id="T2-url2-interne-legitime"),
    # dépendance inter-modules : chaque responsable peut la supprimer
    pytest.param(TEACHER_1, 1, (101, 200), True, id="T1-url1-croise"),
    pytest.param(TEACHER_2, 2, (101, 200), True, id="T2-url2-croise"),
    # URL de son module, dépendance qui ne le concerne pas : la faille
    pytest.param(TEACHER_1, 1, (200, 201), False, id="T1-url1-dependance-etrangere"),
    pytest.param(TEACHER_2, 2, (100, 101), False, id="T2-url2-dependance-etrangere"),
    # URL du module de l'autre
    pytest.param(TEACHER_1, 2, (200, 201), False, id="T1-url2-module-etranger"),
    pytest.param(TEACHER_2, 1, (100, 101), False, id="T2-url1-module-etranger"),
    pytest.param(TEACHER_2, 1, (101, 200), False, id="T2-url1-croise-module-etranger"),
]


@pytest.mark.parametrize("user, url_module, pair, allowed", DELETE_MATRIX)
def test_delete_dependency_ownership(
    call_as: CallAs,
    db_deps: sqlite3.Connection,
    user: User,
    url_module: int,
    pair: tuple[int, int],
    allowed: bool,
) -> None:
    prev, nxt = pair
    assert dep_count(db_deps, prev, nxt) == 1  # garde-fou sur le jeu de données

    call_as(user, "DELETE", f"/modules/{url_module}/dependencies/{prev}/{nxt}")

    assert dep_count(db_deps, prev, nxt) == (0 if allowed else 1), (
        f"{user.prenom} (module {url_module} dans l'URL) : résultat inattendu sur la dépendance "
        f"{pair}"
    )
    # Détecte un DELETE au WHERE trop large : seule la ligne visée peut disparaître
    assert dep_count(db_deps) == (2 if allowed else 3)


# ─────────────────────────────────────────────
# Collision d'ids entre tables et module inexistant
# ─────────────────────────────────────────────


def test_student_with_same_id_as_responsable_cannot_add_dependency(
    call_as: CallAs, db_deps: sqlite3.Connection
) -> None:
    r = call_as(
        STUDENT_1,
        "POST",
        "/modules/1/dependencies",
        json={"id_sequence_prev": 101, "id_sequence_next": 100},
    )

    assert r.status_code == 403
    assert dep_count(db_deps, 101, 100) == 0


def test_student_with_same_id_as_responsable_cannot_delete_dependency(
    call_as: CallAs, db_deps: sqlite3.Connection
) -> None:
    call_as(STUDENT_1, "DELETE", "/modules/1/dependencies/100/101")

    assert dep_count(db_deps, 100, 101) == 1


def test_add_dependency_unknown_module_is_denied_not_500(
    call_as: CallAs, db_deps: sqlite3.Connection
) -> None:
    r = call_as(
        TEACHER_1,
        "POST",
        "/modules/999/dependencies",
        json={"id_sequence_prev": 101, "id_sequence_next": 100},
    )

    assert r.status_code in (403, 404)  # aujourd'hui : IndexError → 500
    assert dep_count(db_deps, 101, 100) == 0
