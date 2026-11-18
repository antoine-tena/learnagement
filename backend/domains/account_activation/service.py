"""Activation d'un compte interne : un lien créé par l'administratif, un mot de passe haché ici.

Les requêtes passent par la connexion de l'appelant, pas par `db_request` : ce dernier
journalise ses paramètres, et l'empreinte du mot de passe n'a rien à faire dans un journal.
"""

from dataclasses import dataclass
from datetime import datetime

import structlog
from sqlalchemy import Connection, text

from auth.authenticate_lnm import password_hash

from .tokens import expiry_from, new_token, token_digest

logger = structlog.get_logger(__name__)

ACCOUNT_TABLES = ("LNM_administratif", "LNM_enseignant", "LNM_etudiant")


@dataclass(frozen=True)
class ActivationToken:
    token: str
    expires_at: datetime


def has_intern_account(conn: Connection, login: str) -> bool:
    """Vrai si un compte interne (hors CAS) porte ce login."""
    for table in ACCOUNT_TABLES:
        found = conn.execute(
            text(f"SELECT 1 FROM {table} WHERE login = :login AND intern_account = 1"),
            {"login": login},
        ).first()
        if found:
            return True
    return False


def create_activation(
    conn: Connection, login: str, id_administratif: int, now: datetime
) -> ActivationToken | None:
    """Un nouveau lien pour `login`, ou None s'il n'a pas de compte interne."""
    if not has_intern_account(conn, login):
        return None
    token = new_token()
    expires_at = expiry_from(now)
    conn.execute(
        text("""
            INSERT INTO LNM_account_activation
                (token_digest, login, id_administratif, expires_at)
            VALUES (:digest, :login, :id_administratif, :expires_at)
        """),
        {
            "digest": token_digest(token),
            "login": login,
            "id_administratif": id_administratif,
            "expires_at": expires_at.replace(tzinfo=None),
        },
    )
    logger.info("account_activation.created", user_id=id_administratif)
    return ActivationToken(token=token, expires_at=expires_at)


def _consume(conn: Connection, digest: str, now: datetime) -> str | None:
    """Marque le jeton utilisé par une mise à jour conditionnelle ; son login, ou None."""
    params = {"digest": digest, "now": now.replace(tzinfo=None)}
    consumed = conn.execute(
        text("""
            UPDATE LNM_account_activation SET used_at = :now
            WHERE token_digest = :digest AND used_at IS NULL AND expires_at > :now
        """),
        params,
    )
    if consumed.rowcount != 1:
        return None
    login: str = conn.execute(
        text("SELECT login FROM LNM_account_activation WHERE token_digest = :digest"), params
    ).scalar_one()
    return login


def activate(conn: Connection, token: str, password: str, now: datetime) -> bool:
    """Pose le mot de passe du compte lié au jeton ; faux si le jeton est inconnu, usé ou expiré."""
    login = _consume(conn, token_digest(token), now)
    if login is None:
        logger.info("account_activation.refused")
        return False
    hashed = password_hash.hash(password)
    for table in ACCOUNT_TABLES:
        conn.execute(
            text(
                f"UPDATE {table} SET password = :hashed WHERE login = :login AND intern_account = 1"
            ),
            {"hashed": hashed, "login": login},
        )
    logger.info("account_activation.done")
    return True
