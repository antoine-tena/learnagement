"""Rendus de module vus par un enseignant (`GET /enseignants/{id}/rendus`)."""

import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import Rows, db_request, get_current_active_user
from core.clock import campus_now
from models.request import SQLRequest
from models.user import User

router = APIRouter()


# Un rendu par promotion concernée, du plus proche au plus lointain.
UPCOMING_RENDUS = """
    SELECT DISTINCT rm.id_rendu_module, rm.date, rm.description, promo.parcour AS promo
    FROM LNM_rendu_module AS rm
        JOIN LNM_rendu_module_as_enseignant AS rm_ens
            ON rm_ens.id_rendu_module = rm.id_rendu_module
        JOIN LNM_rendu_module_as_etudiant AS rm_etu
            ON rm_etu.id_rendu_module = rm.id_rendu_module
        JOIN LNM_etudiant AS etu ON etu.id_etudiant = rm_etu.id_etudiant
        JOIN LNM_promo AS promo ON promo.id_promo = etu.id_promo
    WHERE rm_ens.id_enseignant = %(id_enseignant)s
        AND rm.date >= %(today)s
    ORDER BY rm.date, promo.parcour
"""


@router.get(
    "/enseignants/{id_enseignant:int}/rendus",
    tags=["enseignant"],
    summary="Teacher's upcoming submissions",
    description="Return the submissions to come of the teacher's modules, one per promotion",
    response_model=None,
)
def get_enseignant_rendus(
    id_enseignant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = SQLRequest(
        request=UPCOMING_RENDUS,
        params={"id_enseignant": id_enseignant, "today": _today()},
        allowedRolesRequester={"roles": [], "owner": {"role": "enseignant", "id": "id_enseignant"}},
    )
    return db_request(current_user, request)


def _today() -> datetime.date:
    return campus_now().date()
