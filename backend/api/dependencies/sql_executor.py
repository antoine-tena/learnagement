"""Exécution des requêtes SQL sécurisées via check_access."""

import re
from typing import Any

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import TimeoutError as PoolTimeout

from access_control.checker import check_access
from core.logging import logger
from models.request import SQLRequest
from models.user import User

_PYFORMAT = re.compile(r"%\((\w+)\)s")


def _to_named(sql: str) -> str:
    """Shim transitoire : %(x)s -> :x (à supprimer après migration des requêtes)."""
    return _PYFORMAT.sub(r":\1", sql)


# Rows of a SQL result, as db_request returns them and the routes send them back.
type Rows = list[dict[str, Any]]


def _execute(conn: Connection, request: SQLRequest) -> Rows:
    result = conn.execute(text(_to_named(request.request)), request.params or {})
    return [dict(r) for r in result.mappings()] if result.returns_rows else []


def db_request(requester: User, request: SQLRequest, conn: Connection | None = None) -> Rows:
    """
    Sans `conn` : une connexion et une transaction pour cette seule requête (comportement actuel).
    Avec `conn` : la requête s'exécute dans la transaction de l'appelant, sans commit ici.
    L'appelant ouvre la transaction avec `with get_connection() as conn:`.
    """
    import api.dependencies as pkg

    if requester:
        logger.info(f"User {requester.id} has role {requester.roles} requests {request}")
    else:
        logger.info(f"Anonymous user requests {request}")

    check_access(request=request, user=requester)

    rows = []

    try:
        if conn is not None:
            return _execute(conn, request)
        with pkg.get_connection() as conn:
            result = conn.execute(text(_to_named(request.request)), request.params or {})
            rows = [dict(r) for r in result.mappings()] if result.returns_rows else []
    except PoolTimeout as e:
        raise HTTPException(status_code=503, detail="Database busy, retry later") from e
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Database request failed") from e
    return rows
