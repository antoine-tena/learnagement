"""Jetons d'activation : aléatoires, à durée limitée, gardés en base par leur seule empreinte."""

import hashlib
import secrets
from datetime import datetime, timedelta

TOKEN_BYTES = 32
ACTIVATION_LIFETIME = timedelta(days=7)


def new_token() -> str:
    """Un jeton imprévisible, sûr dans une URL."""
    return secrets.token_urlsafe(TOKEN_BYTES)


def token_digest(token: str) -> str:
    """L'empreinte SHA-256 du jeton, la seule forme gardée en base."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def expiry_from(now: datetime) -> datetime:
    """La fin de validité d'un jeton créé à `now` (UTC)."""
    return now + ACTIVATION_LIFETIME
