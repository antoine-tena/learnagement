"""Paquet d'initialisation des vues MySQL ExplicitSecondaryKs."""

import dotenv

dotenv.load_dotenv(".env")

from .introspection import (  # noqa: E402
    DATABASE,
    HOST,
    PASSWORD,
    USER,
    Connection,
    get_foreign_keys,
    get_primary_key_fields,
    get_secondary_key_fields,
    request,
)
from .queries import requests  # noqa: E402
from .views import build_secondary_key_request, init  # noqa: E402

__all__ = [
    "DATABASE",
    "HOST",
    "PASSWORD",
    "USER",
    "Connection",
    "build_secondary_key_request",
    "get_foreign_keys",
    "get_primary_key_fields",
    "get_secondary_key_fields",
    "init",
    "request",
    "requests",
]
