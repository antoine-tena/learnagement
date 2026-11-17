from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_current_active_user
from db.connection import get_connection
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.delete(
    "/university/etudiant/{id_etudiant:int}/wish/{id_partner_university:int}/semestre/{id_semestre:int}",
    tags=["mobility"],
    summary="Delete university from wishes",
    description="Delete a partner university from the student's mobility wishes",
    response_model=None,
)
def delete_university_from_wishes(
    id_etudiant: int,
    id_partner_university: int,
    id_semestre: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    if current_user.id != id_etudiant:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    allowed = {
        "roles": [],
        "owner": {"role": "etudiant", "id": "id_etudiant"},
    }
    with get_connection() as conn:
        request = {
            "request": """
                            SELECT priority, submission_date
                            FROM MOB_wishes
                            WHERE id_etudiant = %(id_etudiant)s
                              AND id_partner_university = %(id_partner_university)s
                              AND id_semestre = %(id_semestre)s
                        """,
            "params": {
                "id_etudiant": id_etudiant,
                "id_partner_university": id_partner_university,
                "id_semestre": id_semestre,
            },
            "allowedRolesRequester": allowed,
        }
        # if(current_user.id == id_etudiant):
        #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

        check_rows = db_request(current_user, SQLRequest(**request), conn=conn)
        if not check_rows:
            raise HTTPException(status_code=404, detail="Voeu introuvable.")

        if check_rows[0].get("submission_date") is not None:
            raise HTTPException(
                status_code=400,
                detail="Vos voeux ont déjà été soumis et ne peuvent plus être modifiés.",
            )

        removed_priority = int(check_rows[0]["priority"])

        request = {
            "request": """
                            DELETE FROM MOB_wishes
                            WHERE id_etudiant = %(id_etudiant)s
                              AND id_partner_university = %(id_partner_university)s
                              AND id_semestre = %(id_semestre)s
                        """,
            "params": {
                "id_etudiant": id_etudiant,
                "id_partner_university": id_partner_university,
                "id_semestre": id_semestre,
            },
            "allowedRolesRequester": allowed,
        }
        # if(current_user.id == id_etudiant):
        #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

        db_request(current_user, SQLRequest(**request), conn=conn)

        request = {
            "request": """
                            UPDATE MOB_wishes
                            SET priority = priority - 1
                            WHERE id_etudiant = %(id_etudiant)s
                              AND priority > %(removed_priority)s
                        """,
            "params": {
                "id_etudiant": id_etudiant,
                "removed_priority": removed_priority,
            },
            "allowedRolesRequester": {
                "roles": [],
                "owner": {"role": "etudiant", "id": "id_etudiant"},
            },
        }

        # if(current_user.id == id_etudiant):
        #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]
        db_request(current_user, SQLRequest(**request), conn=conn)

    return {"message": "Voeu supprime."}


@router.post(
    "/university/etudiant/{id_etudiant:int}/wish/{id_partner_university:int}/semestre/{id_semestre:int}/move/{direction}",
    tags=["mobility"],
    summary="Move university wish",
    description="Move a wish up or down in the student's priority list",
    response_model=None,
)
def move_university_wish(
    id_etudiant: int,
    id_partner_university: int,
    id_semestre: int,
    direction: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    # if current_user.id != id_etudiant:
    #     raise HTTPException(status_code=403, detail="Unauthorized access")
    allowed = {
        "roles": [],
        "owner": {"role": "etudiant", "id": "id_etudiant"},
    }

    if direction not in ["up", "down"]:
        raise HTTPException(status_code=400, detail="Direction invalide. Utilisez 'up' ou 'down'.")

    with get_connection() as conn:
        request = {
            "request": """
                            SELECT priority, submission_date
                            FROM MOB_wishes
                            WHERE id_etudiant = %(id_etudiant)s
                              AND id_partner_university = %(id_partner_university)s
                              AND id_semestre = %(id_semestre)s
                        """,
            "params": {
                "id_etudiant": id_etudiant,
                "id_partner_university": id_partner_university,
                "id_semestre": id_semestre,
            },
            "allowedRolesRequester": allowed,
        }
        # if(current_user.id == id_etudiant):
        #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]
        current_rows = db_request(current_user, SQLRequest(**request), conn=conn)
        if not current_rows:
            raise HTTPException(status_code=404, detail="Voeu introuvable.")

        if current_rows[0].get("submission_date") is not None:
            raise HTTPException(
                status_code=400,
                detail="Vos voeux ont déjà été soumis et ne peuvent plus être modifiés.",
            )

        current_priority = int(current_rows[0]["priority"])
        target_priority = current_priority - 1 if direction == "up" else current_priority + 1

        request = {
            "request": """
                            SELECT id_partner_university, id_semestre
                            FROM MOB_wishes
                            WHERE id_etudiant = %(id_etudiant)s
                              AND priority = %(target_priority)s
                        """,
            "params": {
                "id_etudiant": id_etudiant,
                "target_priority": target_priority,
            },
            "allowedRolesRequester": allowed,
        }
        # if(current_user.id == id_etudiant):
        #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

        target_rows = db_request(current_user, SQLRequest(**request), conn=conn)
        if not target_rows:
            raise HTTPException(status_code=400, detail="Impossible de deplacer ce voeu plus loin.")

        target_id_partner_university = int(target_rows[0]["id_partner_university"])
        target_id_semestre = int(target_rows[0]["id_semestre"])

        # Step 1: move current wish to a temporary priority to avoid unique collisions.
        request = {
            "request": """
                            UPDATE MOB_wishes
                            SET priority = 0
                            WHERE id_etudiant = %(id_etudiant)s
                              AND id_partner_university = %(current_id_partner_university)s
                              AND id_semestre = %(id_semestre)s
                        """,
            "params": {
                "id_etudiant": id_etudiant,
                "current_id_partner_university": id_partner_university,
                "id_semestre": id_semestre,
            },
            "allowedRolesRequester": allowed,
        }
        # if(current_user.id == id_etudiant):
        #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]
        db_request(current_user, SQLRequest(**request), conn=conn)

        # Step 2: move target wish into current position.
        request = {
            "request": """
                            UPDATE MOB_wishes
                            SET priority = %(current_priority)s
                            WHERE id_etudiant = %(id_etudiant)s
                              AND id_partner_university = %(target_id_partner_university)s
                              AND id_semestre = %(target_id_semestre)s
                        """,
            "params": {
                "id_etudiant": id_etudiant,
                "target_id_partner_university": target_id_partner_university,
                "target_id_semestre": target_id_semestre,
                "current_priority": current_priority,
            },
            "allowedRolesRequester": allowed,
        }
        # if(current_user.id == id_etudiant):
        #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]
        db_request(current_user, SQLRequest(**request), conn=conn)

        # Step 3: move current wish from temporary value to target position.
        request = {
            "request": """
                            UPDATE MOB_wishes
                            SET priority = %(target_priority)s
                            WHERE id_etudiant = %(id_etudiant)s
                              AND id_partner_university = %(current_id_partner_university)s
                              AND id_semestre = %(id_semestre)s
                              AND priority = 0
                        """,
            "params": {
                "id_etudiant": id_etudiant,
                "current_id_partner_university": id_partner_university,
                "id_semestre": id_semestre,
                "target_priority": target_priority,
            },
            "allowedRolesRequester": allowed,
        }
        # if(current_user.id == id_etudiant):
        #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]
        db_request(current_user, SQLRequest(**request), conn=conn)

    return {"message": "Voeu deplace.", "direction": direction}
