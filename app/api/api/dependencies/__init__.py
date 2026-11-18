"""Paquet des dépendances partagées FastAPI et exécution SQL."""

import dotenv

from core.logging import logger
from db.connection import get_connection

from .auth_deps import (
    get_current_active_user,
    get_current_user,
    get_query_token,
    get_token_header,
)
from .sql_executor import Rows, db_request
from .user_loader import (
    _fetch_administratif,
    _fetch_enseignant,
    _fetch_etudiant,
    get_user,
    load_enseignant_responsibilities,
)

dotenv.load_dotenv("../.env")


def main() -> bool:
    return True


__all__ = [
    "Rows",
    "_fetch_administratif",
    "_fetch_enseignant",
    "_fetch_etudiant",
    "db_request",
    "get_connection",
    "get_current_active_user",
    "get_current_user",
    "get_query_token",
    "get_token_header",
    "get_user",
    "load_enseignant_responsibilities",
    "logger",
    "main",
]
