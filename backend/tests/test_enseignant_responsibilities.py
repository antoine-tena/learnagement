"""Les routes reprises de refactor/nextJS_front : qui peut lire quoi, et ce qu'elles renvoient."""

import re
import sqlite3
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from access_control.checker import check_access
from api.dependencies import Rows, get_current_active_user
from domains import lnm_enseignant, maquette_module
from models.request import SQLRequest
from models.user import User

SCHEMA = """
CREATE TABLE LNM_enseignant (id_enseignant INTEGER PRIMARY KEY);
CREATE TABLE LNM_filiere (id_filiere INTEGER PRIMARY KEY, nom_filiere TEXT, nom_long TEXT);
CREATE TABLE LNM_promo (id_promo INTEGER PRIMARY KEY, id_filiere INTEGER);
CREATE TABLE MAQUETTE_learning_unit (id_learning_unit INTEGER PRIMARY KEY, id_promo INTEGER);
CREATE TABLE MAQUETTE_module (
    id_module INTEGER PRIMARY KEY, code_module TEXT, nom TEXT, id_responsable INTEGER);
CREATE TABLE MAQUETTE_module_as_learning_unit (id_module INTEGER, id_learning_unit INTEGER);
CREATE TABLE APC_apprentissage_critique (
    id_apprentissage_critique INTEGER PRIMARY KEY, libelle_apprentissage TEXT);
CREATE TABLE APC_apprentissage_critique_as_module (
    id_apprentissage_critique INTEGER, id_module INTEGER);

INSERT INTO LNM_enseignant VALUES (1), (2);
INSERT INTO LNM_filiere VALUES (5, 'IDU', 'Informatique'), (6, 'MM', 'Mecanique');
INSERT INTO LNM_promo VALUES (50, 5), (60, 6);
INSERT INTO MAQUETTE_learning_unit VALUES (500, 50), (600, 60);
INSERT INTO MAQUETTE_module VALUES (1, 'INFO1', 'Reseaux', 1), (2, 'MECA1', 'Statique', 2);
INSERT INTO MAQUETTE_module_as_learning_unit VALUES (1, 500), (2, 600);
INSERT INTO APC_apprentissage_critique VALUES (9, 'Concevoir');
INSERT INTO APC_apprentissage_critique_as_module VALUES (9, 1);
"""


def make_user(id_: int, role: str) -> User:
    return User(
        id=id_,
        prenom="Test",
        nom="Test",
        ExplicitSecondaryK=f"user{id_}",
        main_role=role,
        roles=["connected_user", role],
    )


TEACHER_1 = make_user(1, "enseignant")
STUDENT_1 = make_user(1, "etudiant")  # même id que TEACHER_1, autre table
HEAD_OF_STUDIES = make_user(3, "responsable_etudes")


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Iterator[FastAPI]:
    conn = sqlite3.connect(":memory:", check_same_thread=False)  # TestClient = autre thread
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)

    def fake_db_request(requester: User, request: SQLRequest) -> Rows:
        check_access(request=request, user=requester)  # vraie règle d'accès
        sql = re.sub(r"%\((\w+)\)s", r":\1", request.request)
        return [dict(row) for row in conn.execute(sql, request.params or {}).fetchall()]

    monkeypatch.setattr(lnm_enseignant, "db_request", fake_db_request)
    monkeypatch.setattr(maquette_module, "db_request", fake_db_request)
    application = FastAPI()
    application.include_router(lnm_enseignant.router)
    application.include_router(maquette_module.router)
    yield application
    conn.close()


def get_as(app: FastAPI, user: User, url: str) -> tuple[int, object]:
    app.dependency_overrides[get_current_active_user] = lambda: user
    response = TestClient(app, raise_server_exceptions=False).get(url)
    return response.status_code, response.json()


def test_teacher_reads_own_modules(app: FastAPI) -> None:
    status, body = get_as(app, TEACHER_1, "/enseignant/1/module_responsabilities")
    assert status == 200
    assert body == [{"id_module": 1, "code_module": "INFO1", "nom": "Reseaux"}]


def test_teacher_reads_own_filieres(app: FastAPI) -> None:
    status, body = get_as(app, TEACHER_1, "/enseignant/1/filieres")
    assert status == 200
    assert body == [{"id_filiere": 5, "nom_filiere": "IDU", "nom_long": "Informatique"}]


@pytest.mark.parametrize("path", ["module_responsabilities", "filieres"])
def test_teacher_cannot_read_a_colleague(app: FastAPI, path: str) -> None:
    status, _ = get_as(app, TEACHER_1, f"/enseignant/2/{path}")
    assert status == 403


@pytest.mark.parametrize("path", ["module_responsabilities", "filieres"])
def test_student_with_same_id_is_refused(app: FastAPI, path: str) -> None:
    status, _ = get_as(app, STUDENT_1, f"/enseignant/1/{path}")
    assert status == 403


@pytest.mark.parametrize("path", ["module_responsabilities", "filieres"])
def test_head_of_studies_reads_any_teacher(app: FastAPI, path: str) -> None:
    status, body = get_as(app, HEAD_OF_STUDIES, f"/enseignant/2/{path}")
    assert status == 200
    assert isinstance(body, list)
    assert len(body) == 1


def test_module_apc(app: FastAPI) -> None:
    status, body = get_as(app, TEACHER_1, "/module/1/apc")
    assert status == 200
    assert body == [{"id_apprentissage_critique": 9, "libelle_apprentissage": "Concevoir"}]
