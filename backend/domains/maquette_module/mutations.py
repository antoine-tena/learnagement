from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from access_control.predicates import is_current_user_module_responsible
from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.post(
    "/modules/{id_module}/sequencage",
    tags=["module"],
    summary="Update module",
    description="Update module according to parameters",
    response_model=None,
)
def add_sequencage(
    id_module: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: dict[str, Any],
) -> Rows:
    required = ["nombre", "id_seance_type", "id_groupe_type", "duree_h"]
    missing = [f for f in required if f not in data or data[f] in (None, "")]
    if missing:
        raise HTTPException(status_code=422, detail=f"Champs manquants : {missing}")

    if (
        "id_intervenant_principal" in data
        and data["id_intervenant_principal"] is not None
        and data["id_intervenant_principal"] != ""
    ):
        request = {
            "request": """
                INSERT INTO MAQUETTE_module_sequencage (
                    id_module,
                    nombre,
                    id_seance_type,
                    id_groupe_type,
                    duree_h,
                    id_intervenant_principal)
                VALUES (
                    %(id_module)s,
                    %(nombre)s,
                    %(id_seance_type)s,
                    %(id_groupe_type)s,
                    %(duree_h)s,
                    %(id_intervenant_principal)s)
            """,
            "params": {
                "id_module": id_module,
                "nombre": data["nombre"],
                "id_seance_type": data["id_seance_type"],
                "id_groupe_type": data["id_groupe_type"],
                "duree_h": data["duree_h"],
                "id_intervenant_principal": data["id_intervenant_principal"],
            },
            "allowedRolesRequester": {
                "roles": [],
                "predicate": is_current_user_module_responsible,
            },
        }
    else:
        request = {
            "request": """
                INSERT INTO MAQUETTE_module_sequencage (
                    id_module,
                    nombre,
                    id_seance_type,
                    id_groupe_type,
                    duree_h)
                VALUES (
                    %(id_module)s,
                    %(nombre)s,
                    %(id_seance_type)s,
                    %(id_groupe_type)s,
                    %(duree_h)s)
            """,
            "params": {
                "id_module": id_module,
                "nombre": data["nombre"],
                "id_seance_type": data["id_seance_type"],
                "id_groupe_type": data["id_groupe_type"],
                "duree_h": data["duree_h"],
            },
            "allowedRolesRequester": {
                "roles": [],
                "predicate": is_current_user_module_responsible,
            },
        }
    return db_request(current_user, SQLRequest(**request))


@router.post(
    "/modules/{id_module}/dependencies",
    tags=["module"],
    summary="Update module",
    description="Update module according to parameters",
    response_model=None,
)
def add_dependencies(
    id_module: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: dict[str, Any],
) -> Rows:
    if "id_sequence_prev" not in data:
        raise HTTPException(status_code=422, detail="Champ manquant : id_sequence_prev")
    if "id_sequence_next" not in data:
        raise HTTPException(status_code=422, detail="Champ manquant : id_sequence_next")

    request = {
        "request": """
            INSERT INTO MAQUETTE_dependance_sequence (id_sequence_prev, id_sequence_next)
                SELECT %(id_sequence_prev)s, %(id_sequence_next)s
                FROM (SELECT 1) AS dummy
                WHERE EXISTS (
                    SELECT 1
                    FROM MAQUETTE_module_sequence ms
                    JOIN MAQUETTE_module_sequencage msg
                      ON msg.id_module_sequencage = ms.id_module_sequencage
                    WHERE msg.id_module = %(id_module)s
                      AND ms.id_module_sequence IN (%(id_sequence_prev)s, %(id_sequence_next)s)
                )
        """,
        "params": {
            "id_sequence_prev": data["id_sequence_prev"],
            "id_sequence_next": data["id_sequence_next"],
            "id_module": id_module,  # required for predicate
        },
        "allowedRolesRequester": {
            "roles": ["responsable_etudes"],
            "predicate": is_current_user_module_responsible,
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.delete(
    "/modules/{id_module}/sequencages/{id_sequencage}",
    tags=["module"],
    summary="Update module",
    description="Update module according to parameters",
    response_model=None,
)
def delete_sequencage(
    id_module: int,
    id_sequencage: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        # ToDo refactor next when SQLAlchemy Core is up
        "request": """
            DELETE FROM MAQUETTE_module_sequencage
            WHERE id_module_sequencage = %(id_sequencage)s  AND
                  id_module = %(id_module)s
        """,
        "params": {
            "id_sequencage": id_sequencage,
            "id_module": id_module,  # required for predicate
        },
        "allowedRolesRequester": {
            "roles": [],
            "predicate": is_current_user_module_responsible,
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.delete(
    "/modules/{id_module}/dependencies/{id_sequence_prev}/{id_sequence_next}",
    tags=["module"],
    summary="Update module",
    description="Update module according to parameters",
    response_model=None,
)
def delete_dependencies(
    id_module: int,
    id_sequence_prev: int,
    id_sequence_next: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        # ToDo refactor next when SQLAlchemy Core is up
        "request": """
            DELETE FROM MAQUETTE_dependance_sequence
            WHERE id_sequence_prev = %(id_sequence_prev)s
                AND id_sequence_next =  %(id_sequence_next)s
                AND (id_sequence_prev IN (
                          SELECT MAQUETTE_module_sequence.id_module_sequence
                          FROM MAQUETTE_module_sequence
                          JOIN MAQUETTE_module_sequencage
                              ON MAQUETTE_module_sequencage.id_module_sequencage
                                  = MAQUETTE_module_sequence.id_module_sequencage
                          WHERE MAQUETTE_module_sequencage.id_module = %(id_module)s
                    )
                    OR id_sequence_next IN (
                          SELECT MAQUETTE_module_sequence.id_module_sequence
                          FROM MAQUETTE_module_sequence
                          JOIN MAQUETTE_module_sequencage
                              ON MAQUETTE_module_sequencage.id_module_sequencage
                                  = MAQUETTE_module_sequence.id_module_sequencage
                          WHERE MAQUETTE_module_sequencage.id_module = %(id_module)s
                    )
                )
        """,
        "params": {
            "id_sequence_prev": id_sequence_prev,
            "id_sequence_next": id_sequence_next,
            "id_module": id_module,  # required for predicate
        },
        "allowedRolesRequester": {
            "roles": [],
            "predicate": is_current_user_module_responsible,
        },
    }
    return db_request(current_user, SQLRequest(**request))
