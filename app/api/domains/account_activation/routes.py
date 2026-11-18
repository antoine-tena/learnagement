from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies import get_current_active_user
from core.rate_limit import ACTIVATION_RATE_LIMIT, limiter
from db.connection import get_connection
from models.user import User

from . import service
from .schemas import ActivationConfirm, ActivationDone, ActivationLink, ActivationRequest

router = APIRouter()

ADMIN_ROLE = "administratif"
INVALID_LINK = "Lien d'activation invalide ou expiré"


@router.post("/account-activation", tags=["auth"], response_model=ActivationLink)
def create_activation_link(
    payload: ActivationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ActivationLink:
    """Un lien d'activation pour un compte interne, créé par un administratif."""
    if ADMIN_ROLE not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    with get_connection() as conn:
        created = service.create_activation(conn, payload.login, current_user.id, datetime.now(UTC))
    if created is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compte interne inconnu")
    return ActivationLink(token=created.token, expires_at=created.expires_at.isoformat())


# Route publique : la personne n'a pas encore de mot de passe. Le jeton (256 bits, usage unique,
# 7 jours) est le seul secret, le débit est limité ; la réponse ne dit jamais si un compte existe.
@router.post("/account-activation/confirm", tags=["auth"], response_model=ActivationDone)
@limiter.limit(ACTIVATION_RATE_LIMIT)
def confirm_activation(request: Request, payload: ActivationConfirm) -> ActivationDone:
    """Pose le mot de passe choisi, haché par l'API."""
    with get_connection() as conn:
        is_activated = service.activate(conn, payload.token, payload.password, datetime.now(UTC))
    if not is_activated:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_LINK)
    return ActivationDone(is_activated=True)
