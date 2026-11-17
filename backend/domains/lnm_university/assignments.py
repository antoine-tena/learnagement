from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Connection

from api.dependencies import get_current_active_user
from db.connection import get_connection
from models.request import SQLRequest
from models.user import User

from ._db import db_request
from .schemas import StudentDecisionPayload, UpdateAssignmentStatusPayload

router = APIRouter()


@router.get(
    "/university/admin/mobility/assigned-students",
    tags=["admin", "mobility"],
    summary="Get list of students who have an assignment",
    response_model=None,
)
def get_assigned_students(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    sql_request = SQLRequest(
        request="""
            SELECT a.id_assignment, a.id_etudiant, a.status, e.nom, e.prenom, e.mail,
                   f.nom_filiere, u.name as university_name
            FROM MOB_assignment a
            JOIN LNM_etudiant e ON a.id_etudiant = e.id_etudiant
            JOIN LNM_promo p ON e.id_promo = p.id_promo
            JOIN LNM_filiere f ON p.id_filiere = f.id_filiere
            JOIN MOB_partner_university u ON a.id_partner_university = u.id_partner_university
            WHERE p.annee = 4
            ORDER BY e.nom ASC, e.prenom ASC
        """,
        params=None,
        allowedRolesRequester=["relations_internationales"],
    )
    result = db_request(current_user, sql_request)
    return result if result else []


@router.post(
    "/university/admin/mobility/update-assignment-status",
    tags=["admin", "mobility"],
    summary="Update assignment status",
    response_model=None,
)
def update_assignment_status(
    payload: UpdateAssignmentStatusPayload,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    if payload.new_status not in ["pending", "accepted", "declined"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    sql_request = SQLRequest(
        request="UPDATE MOB_assignment SET status = %(status)s WHERE id_assignment = %(id)s",
        params={"status": payload.new_status, "id": payload.id_assignment},
        allowedRolesRequester=["relations_internationales"],
    )
    db_request(current_user, sql_request)
    return {"message": "Assignment status updated successfully"}


def sync_db_remaining_places(current_user: User, conn: Connection | None = None) -> None:
    """
    Recalculates the remaining places for all universities and specialties based
    strictly on the number of 'accepted' assignments.
    """
    allowed = ["relations_internationales"]
    query1 = """
        UPDATE MOB_partner_university u
        SET S8_remaining_places = IFNULL(u.S8_total_places, 0) - (
            SELECT COUNT(*)
            FROM MOB_assignment a
            WHERE a.id_partner_university = u.id_partner_university
              AND a.id_semestre = 8
              AND a.status = 'accepted'
        ),
        S9_remaining_places = IFNULL(u.S9_total_places, 0) - (
            SELECT COUNT(*)
            FROM MOB_assignment a
            WHERE a.id_partner_university = u.id_partner_university
              AND a.id_semestre = 9
              AND a.status = 'accepted'
        )
    """

    query2 = """
        UPDATE MOB_partner_university_places p
        SET p.remaining_places = p.number_of_places - (
            SELECT COUNT(*)
            FROM MOB_assignment a
            JOIN LNM_etudiant e ON a.id_etudiant = e.id_etudiant
            JOIN LNM_promo pr ON e.id_promo = pr.id_promo
            WHERE a.id_partner_university = p.id_partner_university
              AND pr.id_filiere = p.id_filiere
              AND p.annee = CASE WHEN a.id_semestre = 8 THEN 4 ELSE 5 END
              AND a.status = 'accepted'
        )
    """
    if conn:
        db_request(
            current_user,
            SQLRequest(request=query1, params=None, allowedRolesRequester=allowed),
            conn=conn,
        )
        db_request(
            current_user,
            SQLRequest(request=query2, params=None, allowedRolesRequester=allowed),
            conn=conn,
        )
    else:
        with get_connection() as conn:
            db_request(
                current_user,
                SQLRequest(request=query1, params=None, allowedRolesRequester=allowed),
                conn=conn,
            )
            db_request(
                current_user,
                SQLRequest(request=query2, params=None, allowedRolesRequester=allowed),
                conn=conn,
            )


@router.get(
    "/university/etudiant/{id_etudiant}/assignment",
    tags=["etudiant", "mobility"],
    summary="Get the assigned university for a student",
    response_model=None,
)
def get_student_assignment(
    id_etudiant: int, current_user: Annotated[User, Depends(get_current_active_user)]
) -> object:
    request = {
        "request": """
            SELECT a.id_assignment, a.status, u.id_partner_university, u.name, u.code, u.country,
                u.address
            FROM MOB_assignment a
            JOIN MOB_partner_university u ON a.id_partner_university = u.id_partner_university
            WHERE a.id_etudiant = %(id_etudiant)s
        """,
        "params": {"id_etudiant": id_etudiant},
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    # if(current_user.id == id_etudiant):
    #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

    result = db_request(current_user, SQLRequest(**request))

    # ToDo Check uncoherent return, does not return all assignments
    if result and len(result) > 0:
        return result[0]
    return None


@router.post(
    "/university/etudiant/{id_etudiant}/assignment/decision",
    tags=["etudiant", "mobility"],
    summary="Submit student decision for assignment",
    response_model=None,
)
def submit_student_decision(
    id_etudiant: int,
    payload: StudentDecisionPayload,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    if current_user.id != id_etudiant:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    if payload.decision not in ["accepted", "declined"]:
        raise HTTPException(
            status_code=400, detail="Invalid decision. Must be 'accepted' or 'declined'."
        )

    # Vérifier que l'affectation existe et est "pending"
    request = {
        "request": """
                    SELECT id_assignment, status
                    FROM MOB_assignment
                    WHERE id_etudiant = %(id_etudiant)s""",
        "params": {"id_etudiant": id_etudiant},
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    # if(current_user.id == id_etudiant):
    #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

    assignment = db_request(current_user, SQLRequest(**request))

    if not assignment or len(assignment) == 0:
        raise HTTPException(status_code=404, detail="Aucune affectation trouvée pour cet étudiant.")

    if assignment[0]["status"] != "pending":
        raise HTTPException(
            status_code=400, detail="La décision a déjà été prise pour cette affectation."
        )

    # Mettre à jour le statut
    request = {
        "request": """
                    UPDATE MOB_assignment
                    SET status = %(status)s
                    WHERE id_etudiant = %(id_etudiant)s""",
        "params": {"status": payload.decision, "id_etudiant": id_etudiant},
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }

    # if(current_user.id == id_etudiant):
    #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]

    db_request(current_user, SQLRequest(**request))

    return {"message": "Décision enregistrée avec succès"}
