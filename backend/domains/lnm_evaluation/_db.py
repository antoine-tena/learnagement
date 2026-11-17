"""Délégation des appels base de données via le paquet lnm_evaluation."""

from sqlalchemy import Connection

from api.dependencies import Rows
from models.request import SQLRequest
from models.user import User


def db_request(
    requester: User | None,
    request: SQLRequest,
    conn: Connection | None = None,
) -> Rows:
    """Délègue à domains.lnm_evaluation.db_request pour préserver les monkeypatches."""
    import domains.lnm_evaluation as pkg

    if conn is None:
        return pkg.db_request(requester, request)
    return pkg.db_request(requester, request, conn=conn)
