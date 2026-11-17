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
TEACHER_2 = make_user(2, "enseignant", "Bernard Responsable2")  # responsable du module 2


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

# (utilisateur, module dans l'URL, module propriétaire de la ressource, attendu)
OWNERSHIP_MATRIX = [
    pytest.param(TEACHER_1, 1, 1, True, id="T1-url1-res1-legitime"),
    pytest.param(TEACHER_2, 2, 2, True, id="T2-url2-res2-legitime"),
    # URL de son module, ressource de l'autre : la faille
    pytest.param(TEACHER_1, 1, 2, False, id="T1-url1-res2-ressource-etrangere"),
    pytest.param(TEACHER_2, 2, 1, False, id="T2-url2-res1-ressource-etrangere"),
    # URL du module de l'autre : il n'est pas responsable de ce module
    pytest.param(TEACHER_1, 2, 2, False, id="T1-url2-res2-module-etranger"),
    pytest.param(TEACHER_2, 1, 1, False, id="T2-url1-res1-module-etranger"),
    # URL du module de l'autre, ressource de son propre module
    pytest.param(TEACHER_1, 2, 1, False, id="T1-url2-res1-croise"),
    pytest.param(TEACHER_2, 1, 2, False, id="T2-url1-res2-croise"),
]


@pytest.mark.parametrize("url, body, check, res_m1, res_m2", PATCH_CASES)
@pytest.mark.parametrize("user, url_module, res_module, allowed", OWNERSHIP_MATRIX)
def test_two_teachers_ownership_matrix(
    call_as: CallAs,
    db: sqlite3.Connection,
    url: str,
    body: dict[str, int],
    check: str,
    res_m1: int,
    res_m2: int,
    user: User,
    url_module: int,
    res_module: int,
    allowed: bool,
) -> None:
    resource = res_m1 if res_module == 1 else res_m2
    before = scalar(db, check.format(r=resource))

    call_as(user, "PATCH", url.format(m=url_module, r=resource), json=body)

    after = scalar(db, check.format(r=resource))
    if allowed:
        assert after == 99, "Le responsable légitime n'a pas pu modifier sa ressource"
    else:
        assert after == before, (
            f"{user.prenom} (module {url_module} dans l'URL) a modifié "
            f"une ressource du module {res_module}"
        )


@pytest.mark.parametrize(
    "user, url_module, res_module, allowed",
    [
        pytest.param(TEACHER_1, 1, 1, True, id="T1-legitime"),
        pytest.param(TEACHER_1, 1, 2, False, id="T1-url1-res2"),
        pytest.param(TEACHER_2, 2, 1, False, id="T2-url2-res1"),
        pytest.param(TEACHER_2, 1, 1, False, id="T2-url1-res1"),
    ],
)
def test_two_teachers_delete_sequencage(
    call_as: CallAs,
    db: sqlite3.Connection,
    user: User,
    url_module: int,
    res_module: int,
    allowed: bool,
) -> None:
    resource = 10 if res_module == 1 else 20

    call_as(user, "DELETE", f"/modules/{url_module}/sequencages/{resource}")

    remaining = scalar(
        db, f"SELECT COUNT(*) FROM MAQUETTE_module_sequencage WHERE id_module_sequencage={resource}"
    )
    assert remaining == (0 if allowed else 1)
