import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import db.connection as dbc
from api.dependencies import db_request
from models.request import SQLRequest


def sql_request(sql: str, params: dict[str, object] | None = None) -> SQLRequest:
    return SQLRequest(request=sql, params=params, allowedRolesRequester="anonymous")


@pytest.fixture(autouse=True)
def sqlite_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    monkeypatch.setattr(dbc, "_engine", engine)
    db_request(None, sql_request("CREATE TABLE t(a INTEGER PRIMARY KEY, b INTEGER)"))


def test_commit_when_all_succeed() -> None:
    with dbc.get_connection() as conn:
        db_request(None, sql_request("INSERT INTO t VALUES (%(a)s, 1)", {"a": 1}), conn=conn)
        db_request(None, sql_request("INSERT INTO t VALUES (%(a)s, 2)", {"a": 2}), conn=conn)
    assert len(db_request(None, sql_request("SELECT * FROM t"))) == 2


def test_rollback_when_one_fails() -> None:
    with pytest.raises(HTTPException) as exc, dbc.get_connection() as conn:
        db_request(None, sql_request("INSERT INTO t VALUES (1, 1)"), conn=conn)
        db_request(None, sql_request("INSERT INTO t VALUES (1, 2)"), conn=conn)  # doublon PK
    assert exc.value.status_code == 500
    assert "UNIQUE" not in exc.value.detail  # pas de fuite SQL
    assert db_request(None, sql_request("SELECT * FROM t")) == []
