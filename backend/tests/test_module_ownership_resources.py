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

# ─────────────────────────────────────────────
# Jeu de données : 2 modules, 2 responsables
#   module 1 (resp. enseignant 1)  →  sequencage 10, sequence 100, session 1000
#   module 2 (resp. enseignant 2)  →  sequencage 20, sequence 200, session 2000
# ─────────────────────────────────────────────

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

# Calls a route as a user: call_as(user, method, url, **request options).
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


TEACHER_1 = make_user(1, "enseignant", "Alice Responsable1")  # responsable du module 1
STUDENT_1 = make_user(1, "etudiant", "Etienne Etudiant")  # même id que TEACHER_1, autre table


@pytest.fixture
def db(monkeypatch: pytest.MonkeyPatch) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:", check_same_thread=False)  # TestClient = autre thread
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)

    def fake_db_request(requester: User, request: SQLRequest) -> Rows:
        check_access(request=request, user=requester)  # vraie règle d'accès
        sql = re.sub(r"%\((\w+)\)s", r":\1", request.request)  # style pyformat → nommé
        cur = conn.execute(sql, request.params or {})
        rows = [dict(r) for r in cur.fetchall()] if cur.description else []
        conn.commit()
        return rows

    monkeypatch.setattr(maquette_module, "db_request", fake_db_request)
    monkeypatch.setattr("api.dependencies.db_request", fake_db_request)  # pour les prédicats
    yield conn
    conn.close()


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


# (url, body, requête de contrôle, id du module 1, id du module 2)
PATCH_CASES = [
    pytest.param(
        "/modules/{m}/sequencages/{r}",
        {"id_intervenant_principal": 99},
        (
            "SELECT id_intervenant_principal FROM MAQUETTE_module_sequencage WHERE "
            "id_module_sequencage={r}"
        ),
        10,
        20,
        id="sequencage",
    ),
    pytest.param(
        "/modules/{m}/sequences/{r}",
        {"id_intervenant_principal": 99},
        (
            "SELECT id_intervenant_principal FROM MAQUETTE_module_sequence WHERE "
            "id_module_sequence={r}"
        ),
        100,
        200,
        id="sequence",
    ),
    pytest.param(
        "/modules/{m}/sessions/{r}",
        {"id_enseignant": 99},
        "SELECT id_enseignant FROM CLASS_session WHERE id_session={r}",
        1000,
        2000,
        id="session",
    ),
]


# ─────────────────────────────────────────────
# Témoin : le cas légitime doit continuer à marcher
# ─────────────────────────────────────────────


@pytest.mark.parametrize("url, body, check, own, foreign", PATCH_CASES)
def test_responsable_can_patch_resource_of_own_module(
    call_as: CallAs,
    db: sqlite3.Connection,
    url: str,
    body: dict[str, int],
    check: str,
    own: int,
    foreign: int,
) -> None:
    r = call_as(TEACHER_1, "PATCH", url.format(m=1, r=own), json=body)
    assert r.status_code == 200
    assert scalar(db, check.format(r=own)) == 99


# ─────────────────────────────────────────────
# Faille : ressource d'un autre module via son propre id_module
# ─────────────────────────────────────────────


@pytest.mark.parametrize("url, body, check, own, foreign", PATCH_CASES)
def test_responsable_cannot_patch_resource_of_other_module(
    call_as: CallAs,
    db: sqlite3.Connection,
    url: str,
    body: dict[str, int],
    check: str,
    own: int,
    foreign: int,
) -> None:
    before = scalar(db, check.format(r=foreign))

    # TEACHER_1 est responsable du module 1 mais cible une ressource du module 2
    call_as(TEACHER_1, "PATCH", url.format(m=1, r=foreign), json=body)

    assert scalar(db, check.format(r=foreign)) == before, (
        "La ressource du module 2 a été modifiée par le responsable du module 1"
    )


def test_responsable_cannot_delete_sequencage_of_other_module(
    call_as: CallAs, db: sqlite3.Connection
) -> None:
    call_as(TEACHER_1, "DELETE", "/modules/1/sequencages/20")

    assert (
        scalar(db, "SELECT COUNT(*) FROM MAQUETTE_module_sequencage WHERE id_module_sequencage=20")
        == 1
    ), "Le séquençage du module 2 a été supprimé par le responsable du module 1"


# ─────────────────────────────────────────────
# Collision d'ids entre tables (autre défaut du même contrôle)
# ─────────────────────────────────────────────


def test_student_with_same_id_as_responsable_is_denied(
    call_as: CallAs, db: sqlite3.Connection
) -> None:
    r = call_as(
        STUDENT_1, "PATCH", "/modules/1/sequences/100", json={"id_intervenant_principal": 99}
    )

    assert r.status_code == 403
    assert (
        scalar(
            db,
            (
                "SELECT id_intervenant_principal FROM MAQUETTE_module_sequence WHERE "
                "id_module_sequence=100"
            ),
        )
        is None
    )


# ─────────────────────────────────────────────
# Robustesse : module inexistant
# ─────────────────────────────────────────────


def test_unknown_module_is_denied_not_500(call_as: CallAs, db: sqlite3.Connection) -> None:
    r = call_as(
        TEACHER_1, "PATCH", "/modules/999/sequences/100", json={"id_intervenant_principal": 99}
    )

    assert r.status_code in (403, 404)  # aujourd'hui : IndexError → 500
