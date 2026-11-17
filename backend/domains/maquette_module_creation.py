"""Création d'un module de la maquette (`POST /modules`)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import Rows, db_request, get_current_active_user
from models.module import ModuleCreation
from models.request import SQLRequest
from models.user import User

router = APIRouter()

MODULE_CREATORS = ["responsable_etudes"]

EXISTING_MODULE = """
    SELECT id_module FROM MAQUETTE_module WHERE code_module = %(code_module)s
"""

INSERT_MODULE = """
    INSERT INTO MAQUETTE_module (
        code_module, nom, hCM, hTD, hTP, hPROJ, hPersonnelle, ECTS,
        id_semestre, id_responsable, id_discipline
    ) VALUES (
        %(code_module)s, %(nom)s, %(hours_cm)s, %(hours_td)s, %(hours_tp)s, %(hours_project)s,
        %(hours_personal)s, %(ects)s, %(id_semestre)s, %(id_responsable)s, %(id_discipline)s
    )
"""


@router.post(
    "/modules",
    tags=["module"],
    summary="Create module",
    description="Create a module of the curriculum; 409 if its code already exists",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
)
def create_module(
    module: ModuleCreation,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    params = module.model_dump()
    if db_request(current_user, _request(EXISTING_MODULE, params)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ce code de module existe déjà")
    return db_request(current_user, _request(INSERT_MODULE, params))


def _request(sql: str, params: dict[str, object]) -> SQLRequest:
    return SQLRequest(request=sql, params=params, allowedRolesRequester=MODULE_CREATORS)
