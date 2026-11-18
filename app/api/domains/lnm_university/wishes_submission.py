from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.post(
    "/university/etudiant/{id_etudiant:int}/wishes/submit",
    tags=["mobility"],
    summary="Submit university wishes",
    description="Submit the student's mobility wishes for processing",
    response_model=None,
)
def submit_university_wishes(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    if current_user.id != id_etudiant:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    request = {
        "request": """
                        SELECT
                            COUNT(*) AS wishes_count,
                            MAX(CASE WHEN submission_date IS NOT NULL THEN 1 ELSE 0
                                END) AS is_submitted
                        FROM MOB_wishes
                        WHERE id_etudiant = %(id_etudiant)s
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
    check_rows = db_request(current_user, SQLRequest(**request))
    wishes_count = int(check_rows[0].get("wishes_count") or 0) if check_rows else 0
    is_submitted = int(check_rows[0].get("is_submitted") or 0) if check_rows else 0

    if is_submitted > 0:
        raise HTTPException(status_code=400, detail="Vos voeux ont déjà été soumis.")

    if wishes_count < 1:
        raise HTTPException(
            status_code=400, detail="Vous devez avoir au moins 1 voeu pour soumettre votre dossier."
        )

    # Update the submission date for all submitted wishes
    request = {
        "request": """
                        UPDATE MOB_wishes
                        SET submission_date = NOW()
                        WHERE id_etudiant = %(id_etudiant)s
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
    db_request(current_user, SQLRequest(**request))

    return {"message": "Voeux soumis avec succes."}


@router.post(
    "/university/admin/wishes/force-submit",
    tags=["admin", "mobility"],
    summary="Force submit all incomplete wishes",
    description=(
        "Force the submission of all existing student wishes that have not been submitted yet."
    ),
    response_model=None,
)
def force_submit_wishes(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    update_request = {
        "request": """
                        UPDATE MOB_wishes
                        SET submission_date = NOW()
                        WHERE submission_date IS NULL
                    """,
        "params": None,
        "allowedRolesRequester": ["relations_internationales"],
    }
    db_request(current_user, SQLRequest(**update_request))
    return {"message": "Tous les voeux incomplets ont ete clotures avec succes."}


@router.get(
    "/university/admin/wishes",
    tags=["mobility"],
    summary="All wishes for RI",
    description=(
        "Return all student wishes (submitted and in progress) for International Relations admins"
    ),
    response_model=None,
)
def list_all_wishes_ri(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                        SELECT
                            e.id_etudiant,
                            e.nom AS etudiant_nom,
                            e.prenom AS etudiant_prenom,
                            e.mail AS etudiant_mail,
                            w.id_wish,
                            w.id_semestre,
                            w.priority,
                            w.submission_date,
                            u.id_partner_university,
                            u.name AS university_name,
                            u.country AS university_country,
                            u.code AS university_code,
                            a.id_assignment,
                            a.status AS assignment_status,
                            f.nom_filiere AS filiere_nom
                        FROM LNM_etudiant e
                        JOIN LNM_promo p ON e.id_promo = p.id_promo
                        LEFT JOIN LNM_filiere f ON p.id_filiere = f.id_filiere
                        LEFT JOIN MOB_wishes w ON e.id_etudiant = w.id_etudiant
                        LEFT JOIN MOB_partner_university u
                            ON u.id_partner_university = w.id_partner_university
                        LEFT JOIN MOB_assignment a ON a.id_etudiant = e.id_etudiant
                        WHERE p.annee = 4
                        ORDER BY e.nom ASC, e.prenom ASC, w.priority ASC
                    """,
        "allowedRolesRequester": ["relations_internationales"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/university/admin/mobility/submitted-students",
    tags=["admin", "mobility"],
    summary="Get list of students who have submitted wishes",
    response_model=None,
)
def get_submitted_students(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    sql_request = SQLRequest(
        request="""
            SELECT e.id_etudiant, e.nom, e.prenom, e.mail, f.nom_filiere
            FROM LNM_etudiant e
            JOIN LNM_promo p ON e.id_promo = p.id_promo
            JOIN LNM_filiere f ON p.id_filiere = f.id_filiere
            WHERE p.annee = 4
              AND EXISTS (
                  SELECT 1 FROM MOB_wishes w
                  WHERE w.id_etudiant = e.id_etudiant
                    AND w.submission_date IS NOT NULL
              )
            ORDER BY e.nom ASC, e.prenom ASC
        """,
        params=None,
        allowedRolesRequester=["relations_internationales"],
    )
    result = db_request(current_user, sql_request)
    return result if result else []


@router.post(
    "/university/admin/mobility/reset-wishes/{id_etudiant}",
    tags=["admin", "mobility"],
    summary="Reset submission date for a student's wishes",
    response_model=None,
)
def reset_student_wishes(
    id_etudiant: int, current_user: Annotated[User, Depends(get_current_active_user)]
) -> object:
    check_request = SQLRequest(
        request="""
            SELECT 1 FROM LNM_etudiant e
            JOIN LNM_promo p ON e.id_promo = p.id_promo
            WHERE e.id_etudiant = %(id)s AND p.annee = 4
        """,
        params={"id": id_etudiant},
        allowedRolesRequester=["relations_internationales"],
    )
    if not db_request(current_user, check_request):
        raise HTTPException(status_code=400, detail="Étudiant invalide ou non éligible.")

    sql_request = SQLRequest(
        request="""
            UPDATE MOB_wishes
            SET submission_date = NULL
            WHERE id_etudiant = %(id)s
        """,
        params={"id": id_etudiant},
        allowedRolesRequester=["relations_internationales"],
    )
    db_request(current_user, sql_request)
    return {"message": "La soumission a été annulée avec succès."}
