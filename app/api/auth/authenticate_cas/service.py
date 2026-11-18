"""Vérification du token de service CAS et authentification JWT."""

import hmac
import os
from typing import Annotated

from fastapi import Header, HTTPException, status

from api.dependencies import logger
from auth.authenticate_tools import create_access_token
from models.token import Token

from .provisioning import _determine_role_from_cas_groups
from .schemas import CasUserProvision


def verify_cas_service_token(x_cas_token: Annotated[str | None, Header()] = None) -> None:
    expected = os.getenv("CAS_SERVICE_TOKEN")

    if not expected:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CAS service token not configured",
        )
    if not x_cas_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing CAS service token",
        )

    try:
        if not hmac.compare_digest(x_cas_token.encode("utf-8"), expected.encode("utf-8")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid CAS service token",
            )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid CAS service token",
        ) from None


async def authenticate_cas(data: CasUserProvision) -> Token:
    """
    Point d'entrée unique pour l'auth CAS.
    Cherche l'user, le crée si premier login, retourne toujours un JWT.
    """
    import auth.authenticate_cas as pkg

    user = pkg.get_user(data.login)
    main_role = ""
    if not user:
        logger.info("auth.cas_first_login")

        main_role = _determine_role_from_cas_groups(data.members)

        if main_role is None:
            logger.error("auth.cas_no_allowed_group", groups=data.members)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'avez pas accès à cette application",
            )

        user = pkg._create_cas_user(data, main_role=main_role)

    if not user:
        logger.error("auth.cas_provisioning_failed", main_role=main_role)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="CAS authentication failed"
        )

    access_token = create_access_token(
        data={
            "id": user.id,
            "login": user.login,
            "email": user.mail,
            "firstname": user.prenom,
            "lastname": user.nom,
            "roles": user.roles,
            "password2update": False,
        },
    )

    logger.info("auth.cas_login", user_id=user.id, roles=user.roles)

    return Token(access_token=access_token, token_type="bearer")
