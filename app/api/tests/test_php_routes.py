"""Routes qui remplacent le SQL des pages PHP : création de module, rendus d'un enseignant."""

import datetime
import re
import sqlite3
from collections.abc import Callable, Iterator
from types import ModuleType

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response

from access_control.checker import check_access
from api.dependencies import Rows, get_current_active_user
from domains import lnm_rendu_module, maquette_module_creation
from models.request import SQLRequest
from models.user import User

TODAY = datetime.date(2026, 11, 17)

SCHEMA = """
CREATE TABLE MAQUETTE_module (
    id_module INTEGER PRIMARY KEY, code_module TEXT UNIQUE, nom TEXT, hCM REAL, hTD REAL,
    hTP REAL, hPROJ REAL, hPersonnelle REAL, ECTS REAL, id_semestre INTEGER,
    id_responsable INTEGER, id_discipline INTEGER);
CREATE TABLE LNM_rendu_module (
    id_rendu_module INTEGER PRIMARY KEY, description TEXT, date TEXT, id_module INTEGER);
CREATE TABLE LNM_rendu_module_as_enseignant (id_rendu_module INTEGER, id_enseignant INTEGER);
CREATE TABLE LNM_rendu_module_as_etudiant (id_rendu_module INTEGER, id_etudiant INTEGER);
CREATE TABLE LNM_etudiant (id_etudiant INTEGER PRIMARY KEY, id_promo INTEGER);
CREATE TABLE LNM_promo (id_promo INTEGER PRIMARY KEY, parcour TEXT);

INSERT INTO MAQUETTE_module (id_module, code_module, nom) VALUES (1, 'INFO501', 'Réseaux');
INSERT INTO LNM_promo VALUES (1, 'IDU3'), (2, 'IDU4');
INSERT INTO LNM_etudiant VALUES (1, 1), (2, 1), (3, 2);
INSERT INTO LNM_rendu_module VALUES
    (10, 'Rapport', '2026-12-01', 1), (11, 'Passé', '2026-11-16', 1),
    (12, 'Autre', '2026-12-02', 1);
INSERT INTO LNM_rendu_module_as_enseignant VALUES (10, 1), (11, 1), (12, 2);
INSERT INTO LNM_rendu_module_as_etudiant VALUES (10, 1), (10, 2), (10, 3), (11, 1), (12, 1);
"""

NEW_MODULE = {
    "code_module": "INFO502",
    "nom": "Bases de données",
    "hCM": 10,
    "hTD": 12,
    "hTP": 8,
    "hProj": 0,
    "hPerso": 20,
    "ECTS": 3,
    "semestre": 5,
    "id_responsable": 1,
    "id_discipline": 2,
}

type CallAs = Callable[..., Response]


def make_user(id_: int, role: str, *extra_roles: str) -> User:
    name = f"{role}{id_}"
    roles = ["connected_user", role, *extra_roles]
    return User(id=id_, prenom=name, nom=name, ExplicitSecondaryK=name, main_role=role, roles=roles)


TEACHER_1 = make_user(1, "enseignant")
HEAD_OF_STUDIES = make_user(2, "enseignant", "responsable_etudes")


@pytest.fixture
def db(monkeypatch: pytest.MonkeyPatch) -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(":memory:", check_same_thread=False)  # TestClient = autre thread
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)

    def fake_db_request(requester: User, request: SQLRequest) -> Rows:
        check_access(request=request, user=requester)  # vraie règle d'accès
        sql = re.sub(r"%\((\w+)\)s", r":\1", request.request)  # style pyformat → nommé
        params = {
            k: str(v) if isinstance(v, datetime.date) else v
            for k, v in (request.params or {}).items()
        }
        cur = conn.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()] if cur.description else []
        conn.commit()
        return rows

    domain: ModuleType
    for domain in (maquette_module_creation, lnm_rendu_module):
        monkeypatch.setattr(domain, "db_request", fake_db_request)
    monkeypatch.setattr(lnm_rendu_module, "_today", lambda: TODAY)
    yield conn
    conn.close()


@pytest.fixture
def call_as(db: sqlite3.Connection) -> CallAs:
    app = FastAPI()
    app.include_router(maquette_module_creation.router)
    app.include_router(lnm_rendu_module.router)
    client = TestClient(app, raise_server_exceptions=False)

    def _call(user: User, method: str, url: str, json: dict[str, object] | None = None) -> Response:
        app.dependency_overrides[get_current_active_user] = lambda: user
        response: Response = client.request(method, url, json=json)
        return response

    return _call


def test_head_of_studies_creates_a_module(call_as: CallAs, db: sqlite3.Connection) -> None:
    response = call_as(HEAD_OF_STUDIES, "POST", "/modules", json=NEW_MODULE)

    assert response.status_code == 201
    row = db.execute("SELECT * FROM MAQUETTE_module WHERE code_module = 'INFO502'").fetchone()
    assert (row["hPROJ"], row["hPersonnelle"], row["ECTS"], row["id_semestre"]) == (0, 20, 3, 5)


def test_a_plain_teacher_cannot_create_a_module(call_as: CallAs, db: sqlite3.Connection) -> None:
    response = call_as(TEACHER_1, "POST", "/modules", json=NEW_MODULE)

    assert response.status_code == 403
    assert db.execute("SELECT COUNT(*) FROM MAQUETTE_module").fetchone()[0] == 1


def test_an_existing_code_is_a_conflict(call_as: CallAs) -> None:
    response = call_as(
        HEAD_OF_STUDIES, "POST", "/modules", json={**NEW_MODULE, "code_module": "INFO501"}
    )

    assert response.status_code == 409


@pytest.mark.parametrize("change", [{"semestre": None}, {"nom": ""}, {"hCM": -1}, {"inconnu": 1}])
def test_an_invalid_module_is_refused(call_as: CallAs, change: dict[str, object]) -> None:
    response = call_as(HEAD_OF_STUDIES, "POST", "/modules", json={**NEW_MODULE, **change})

    assert response.status_code == 422


def test_a_teacher_sees_their_upcoming_rendus_once_per_promo(call_as: CallAs) -> None:
    response = call_as(TEACHER_1, "GET", "/enseignants/1/rendus")

    assert response.status_code == 200
    assert [(r["description"], r["promo"]) for r in response.json()] == [
        ("Rapport", "IDU3"),
        ("Rapport", "IDU4"),
    ]


def test_a_teacher_cannot_read_another_teachers_rendus(call_as: CallAs) -> None:
    response = call_as(TEACHER_1, "GET", "/enseignants/2/rendus")

    assert response.status_code == 403
