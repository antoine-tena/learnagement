"""Délégation des appels base de données via le paquet lnm_mobility_assignment."""

from contextlib import AbstractContextManager

from sqlalchemy import Connection

from api.dependencies import Rows
from models.request import SQLRequest
from models.user import User


def db_request(
    requester: User | None,
    request: SQLRequest,
    conn: Connection | None = None,
) -> Rows:
    """Délègue à domains.lnm_mobility_assignment.db_request pour préserver les monkeypatches."""
    import domains.lnm_mobility_assignment as pkg

    if conn is None:
        return pkg.db_request(requester, request)
    return pkg.db_request(requester, request, conn=conn)


def get_connection() -> AbstractContextManager[Connection]:
    """Délègue à domains.lnm_mobility_assignment.get_connection."""
    import domains.lnm_mobility_assignment as pkg

    return pkg.get_connection()
