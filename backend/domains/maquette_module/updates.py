from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from access_control.predicates import is_current_user_module_responsible
from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.patch(
    "/module/{id_module}",
    tags=["module"],
    summary="Update module",
    description="Update module according to parameters",
    response_model=None,
)
def update_module(
    id_module: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: dict[str, Any],
) -> Rows:
    if "id_responsable" not in data:
        raise HTTPException(status_code=422, detail="Champ manquant : id_responsable")

    request = {
        "request": """
            UPDATE MAQUETTE_module
            SET id_responsable = %(id_responsable)s
            WHERE id_module = %(id_module)s
        """,
        "params": {
            "id_responsable": data["id_responsable"],
            "id_module": id_module,
        },
        "allowedRolesRequester": {
            "roles": ["responsable_etudes"],
            "predicate": is_current_user_module_responsible,
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.patch(
    "/modules/{id_module}/sequencages/{id_sequencage}",
    tags=["module"],
    summary="Update sequencage",
    description="Update sequencage according to parameters",
    response_model=None,
)
def update_sequencage(
    id_module: int,
    id_sequencage: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: dict[str, Any],
) -> Rows:
    if "id_intervenant_principal" not in data:
        raise HTTPException(status_code=422, detail="Champ manquant : id_intervenant_principal")

    request = {
        # ToDo refactor when SQLAlchemy Core is up
        "request": """
            UPDATE MAQUETTE_module_sequencage
            SET id_intervenant_principal = %(id_intervenant_principal)s
            WHERE id_module_sequencage = %(id_sequencage)s  AND
                  id_module = %(id_module)s
        """,
        "params": {
            "id_intervenant_principal": data["id_intervenant_principal"],
            "id_sequencage": id_sequencage,
            "id_module": id_module,  # required for predicate
        },
        "allowedRolesRequester": {
            "roles": [],
            "predicate": is_current_user_module_responsible,
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.patch(
    "/modules/{id_module}/sequences/{id_sequence}",
    tags=["module"],
    summary="Update sequencage",
    description="Update sequencage according to parameters",
    response_model=None,
)
def update_sequence(
    id_module: int,
    id_sequence: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: dict[str, Any],
) -> Rows:
    if "id_intervenant_principal" not in data:
        raise HTTPException(status_code=422, detail="Champ manquant : id_intervenant_principal")

    request = {
        # ToDo refactor when SQLAlchemy Core is up
        "request": """
               UPDATE MAQUETTE_module_sequence
               SET id_intervenant_principal = %(id_intervenant_principal)s
               WHERE id_module_sequence = %(id_sequence)s AND
                     id_module_sequencage IN (
                          SELECT MAQUETTE_module_sequencage.id_module_sequencage
                          FROM  MAQUETTE_module_sequencage
                          WHERE MAQUETTE_module_sequencage.id_module = %(id_module)s
                     )
           """,
        "params": {
            "id_intervenant_principal": data["id_intervenant_principal"],
            "id_sequence": id_sequence,
            "id_module": id_module,  # required for predicate
        },
        "allowedRolesRequester": {
            "roles": [],
            "predicate": is_current_user_module_responsible,
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.patch(
    "/modules/{id_module}/sessions/{id_session}",
    tags=["module"],
    summary="Update sequencage",
    description="Update sequencage according to parameters",
    response_model=None,
)
def update_session(
    id_module: int,
    id_session: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: dict[str, Any],
) -> Rows:
    if "id_enseignant" not in data:
        raise HTTPException(status_code=422, detail="Champ manquant : id_enseignant")

    request = {
        # ToDo refactor when SQLAlchemy Core is up
        "request": """
               UPDATE CLASS_session
               SET id_enseignant = %(id_enseignant)s
               WHERE id_session = %(id_session)s AND
                     id_module_sequence IN (
                          SELECT MAQUETTE_module_sequence.id_module_sequence
                          FROM MAQUETTE_module_sequence
                          JOIN MAQUETTE_module_sequencage
                              ON MAQUETTE_module_sequencage.id_module_sequencage
                                  = MAQUETTE_module_sequence.id_module_sequencage
                          WHERE MAQUETTE_module_sequencage.id_module = %(id_module)s
                     )
           """,
        "params": {
            "id_enseignant": data["id_enseignant"],
            "id_session": id_session,
            "id_module": id_module,  # required for predicate
        },
        "allowedRolesRequester": {
            "roles": [],
            "predicate": is_current_user_module_responsible,
        },
    }
    return db_request(current_user, SQLRequest(**request))
