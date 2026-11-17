from sqlalchemy import Connection

from api.dependencies import Rows
from models.request import SQLRequest
from models.user import User


def db_request(
    requester: User | None,
    request: SQLRequest,
    conn: Connection | None = None,
) -> Rows:
    """Relais vers le package pour préserver le monkeypatching des tests."""
    import domains.lnm_university as pkg

    return pkg.db_request(requester, request, conn=conn)
