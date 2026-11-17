"""Paquet d'authentification et de provisionnement CAS."""

from api.dependencies import get_user, logger
from db.connection import get_connection

from .provisioning import (
    _create_cas_user,
    _determine_promo_from_cas_groups,
    _determine_role_from_cas_groups,
)
from .schemas import CasUserProvision
from .service import authenticate_cas, verify_cas_service_token

__all__ = [
    "CasUserProvision",
    "_create_cas_user",
    "_determine_promo_from_cas_groups",
    "_determine_role_from_cas_groups",
    "authenticate_cas",
    "get_connection",
    "get_user",
    "logger",
    "verify_cas_service_token",
]
