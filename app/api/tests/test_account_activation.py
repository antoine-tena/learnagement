from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.pool import StaticPool

from api.dependencies import get_current_active_user
from app import app
from auth.authenticate_lnm import verify_password
from domains.account_activation import service
from domains.account_activation.tokens import token_digest
from models.user import User

NOW = datetime(2026, 11, 18, 9, 0, tzinfo=UTC)
PASSWORD = "un-mot-de-passe-solide"
SCHEMA = [
    "CREATE TABLE LNM_account_activation (id_account_activation INTEGER PRIMARY KEY, "
    "token_digest TEXT, login TEXT, id_administratif INT, expires_at DATETIME, used_at DATETIME)",
    *(
        f"CREATE TABLE {table} (login TEXT, intern_account INT, password TEXT)"
        for table in service.ACCOUNT_TABLES
    ),
    "INSERT INTO LNM_etudiant VALUES ('jdupont', 1, NULL)",
    "INSERT INTO LNM_etudiant VALUES ('cas_user', 0, NULL)",
]


@pytest.fixture
def engine() -> Engine:
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    with engine.begin() as conn:
        for statement in SCHEMA:
            conn.execute(text(statement))
    return engine


def stored_password(conn: Connection) -> str | None:
    password: str | None = conn.execute(
        text("SELECT password FROM LNM_etudiant WHERE login = 'jdupont'")
    ).scalar()
    return password


def test_activation_hashes_the_password_on_the_server(engine: Engine) -> None:
    with engine.begin() as conn:
        created = service.create_activation(conn, "jdupont", 1, NOW)
        assert created is not None
        assert service.activate(conn, created.token, PASSWORD, NOW + timedelta(days=1))
        hashed = stored_password(conn)
    assert hashed is not None and hashed != PASSWORD
    assert verify_password(PASSWORD, hashed)


def test_token_is_stored_only_as_its_digest(engine: Engine) -> None:
    with engine.begin() as conn:
        created = service.create_activation(conn, "jdupont", 1, NOW)
        assert created is not None
        digests = conn.execute(text("SELECT token_digest FROM LNM_account_activation")).scalars()
        assert list(digests) == [token_digest(created.token)]


def test_token_works_once(engine: Engine) -> None:
    with engine.begin() as conn:
        created = service.create_activation(conn, "jdupont", 1, NOW)
        assert created is not None
        assert service.activate(conn, created.token, PASSWORD, NOW)
        assert not service.activate(conn, created.token, "un-autre-mot-de-passe", NOW)


def test_expired_token_is_refused(engine: Engine) -> None:
    with engine.begin() as conn:
        created = service.create_activation(conn, "jdupont", 1, NOW)
        assert created is not None
        assert not service.activate(conn, created.token, PASSWORD, NOW + timedelta(days=8))
        assert stored_password(conn) is None


def test_cas_account_gets_no_link(engine: Engine) -> None:
    with engine.begin() as conn:
        assert service.create_activation(conn, "cas_user", 1, NOW) is None


def make_user(roles: list[str]) -> User:
    return User(id=1, prenom="A", nom="B", ExplicitSecondaryK="k", main_role=roles[0], roles=roles)


@pytest.fixture
def client(engine: Engine) -> Iterator[TestClient]:
    @contextmanager
    def connection() -> Iterator[Connection]:
        with engine.begin() as conn:
            yield conn

    with patch("domains.account_activation.routes.get_connection", connection):
        yield TestClient(app)
    app.dependency_overrides.clear()


def test_student_cannot_create_a_link(client: TestClient) -> None:
    app.dependency_overrides[get_current_active_user] = lambda: make_user(["etudiant"])
    response = client.post("/account-activation", json={"login": "jdupont"})
    assert response.status_code == 403


def test_anonymous_cannot_create_a_link(client: TestClient) -> None:
    assert client.post("/account-activation", json={"login": "jdupont"}).status_code == 401


def test_link_then_confirm_through_the_api(client: TestClient, engine: Engine) -> None:
    app.dependency_overrides[get_current_active_user] = lambda: make_user(["administratif"])
    token = client.post("/account-activation", json={"login": "jdupont"}).json()["token"]
    confirm = {"token": token, "password": PASSWORD}
    assert client.post("/account-activation/confirm", json=confirm).status_code == 200
    with engine.begin() as conn:
        hashed = stored_password(conn)
    assert hashed is not None and verify_password(PASSWORD, hashed)


def test_unknown_token_is_refused(client: TestClient) -> None:
    confirm = {"token": "inconnu", "password": PASSWORD}
    assert client.post("/account-activation/confirm", json=confirm).status_code == 400


def test_short_password_is_refused(client: TestClient) -> None:
    confirm = {"token": "inconnu", "password": "court"}
    assert client.post("/account-activation/confirm", json=confirm).status_code == 422
