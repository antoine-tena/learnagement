from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException

from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.get(
    "/university/etudiant/{id_etudiant:int}/campaign-status",
    tags=["mobility"],
    summary="Statut de la campagne pour l'étudiant",
    description="Indique si la campagne de mobilité est ouverte pour cet étudiant",
    response_model=None,
)
def get_campaign_status(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    request = {
        "request": """
                    SELECT mobility_z_score
                    FROM LNM_etudiant
                    WHERE id_etudiant = %(id_etudiant)s""",
        "params": {"id_etudiant": id_etudiant},
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }

    # if(current_user.id == id_etudiant):
    #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

    result = db_request(current_user, SQLRequest(**request))

    is_open = bool(result and result[0].get("mobility_z_score") is not None)
    return {"is_open": is_open}


@router.get(
    "/university/etudiant/{id_etudiant:int}/wishes",
    tags=["mobility"],
    summary="Wishes for student",
    description="Return the student's current mobility wishes",
    response_model=None,
)
def list_university_wishes_etudiant(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    if current_user.id != id_etudiant:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    request = {
        "request": """
                        SELECT w.priority, w.submission_date, w.id_semestre, u.*
                        FROM MOB_wishes w
                        JOIN MOB_partner_university u
                            ON u.id_partner_university = w.id_partner_university
                        WHERE w.id_etudiant = %(id_etudiant)s
                        ORDER BY w.priority ASC
                    """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    # if(current_user.id == id_etudiant):
    #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

    return db_request(current_user, SQLRequest(**request))


@router.post(
    "/university/etudiant/{id_etudiant:int}/wish/{id_partner_university:int}",
    tags=["mobility"],
    summary="Add university to wishes",
    description="Add a partner university to the student's mobility wishes",
    response_model=None,
)
def add_university_to_wishes(
    id_etudiant: int,
    id_partner_university: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    payload: Annotated[dict | None, Body()] = None,
) -> Rows:
    if current_user.id != id_etudiant:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    # Le frontend envoie directement l'id_semestre correspondant au choix
    id_semestre = payload.get("id_semestre", 8) if payload else 8

    # Sécurité : bloquer l'ajout de vœux si la campagne n'est pas encore ouverte
    request = {
        "request": """
                    SELECT mobility_z_score
                    FROM LNM_etudiant
                    WHERE id_etudiant = %(id_etudiant)s""",
        "params": {"id_etudiant": id_etudiant},
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    # if(current_user.id == id_etudiant):
    #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

    student_data = db_request(current_user, SQLRequest(**request))

    if not student_data or student_data[0].get("mobility_z_score") is None:
        raise HTTPException(
            status_code=403,
            detail=(
                "La campagne de mobilité n'est pas encore ouverte. Vous ne pouvez pas ajouter "
                "de vœux."
            ),
        )

    request = {
        "request": """
                        SELECT
                            COUNT(*) AS wishes_count,
                            COALESCE(MAX(priority), 0) AS max_priority,
                            COALESCE(SUM(CASE WHEN id_partner_university = %(id_partner_university)s
                                AND id_semestre = %(id_semestre)s THEN 1 ELSE 0
                                END), 0) AS already_exists,
                            MAX(CASE WHEN submission_date IS NOT NULL THEN 1 ELSE 0
                                END) AS is_submitted
                        FROM MOB_wishes
                        WHERE id_etudiant = %(id_etudiant)s
                    """,
        "params": {
            "id_etudiant": id_etudiant,
            "id_partner_university": id_partner_university,
            "id_semestre": id_semestre,
        },
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    # if(current_user.id == id_etudiant):
    #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

    check_rows = db_request(current_user, SQLRequest(**request))
    wishes_count = int(check_rows[0].get("wishes_count") or 0) if check_rows else 0
    max_priority = int(check_rows[0].get("max_priority") or 0) if check_rows else 0
    already_exists = int(check_rows[0].get("already_exists") or 0) if check_rows else 0
    is_submitted = int(check_rows[0].get("is_submitted") or 0) if check_rows else 0

    if is_submitted > 0:
        raise HTTPException(
            status_code=400,
            detail="Vos voeux ont déjà été soumis et ne peuvent plus être modifiés.",
        )

    if wishes_count >= 5:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas ajouter plus de 5 voeux.")

    if already_exists > 0:
        raise HTTPException(
            status_code=400, detail="Cette universite est deja dans vos voeux pour ce semestre."
        )

    next_priority = max_priority + 1

    request = {
        "request": """
                        INSERT INTO MOB_wishes (id_etudiant, id_partner_university, priority,
                            id_semestre)
                        VALUES (%(id_etudiant)s, %(id_partner_university)s, %(priority)s,
                            %(id_semestre)s)
                    """,
        "params": {
            "id_etudiant": id_etudiant,
            "id_partner_university": id_partner_university,
            "priority": next_priority,
            "id_semestre": id_semestre,
        },
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    # if(current_user.id == id_etudiant):
    #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

    return db_request(current_user, SQLRequest(**request))
