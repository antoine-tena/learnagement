from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.get(
    "/university",
    tags=["mobility"],
    summary="Universities",
    description="Return the list of partner universities",
    response_model=None,
)
def list_universities(
    # current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                        SELECT * FROM MOB_partner_university
                    """,
        "allowedRolesRequester": "anonymous",
    }
    # return db_request(current_user, SQLRequest(**request))
    return db_request(None, SQLRequest(**request))


@router.get(
    "/university/etudiant/{id_etudiant:int}",
    tags=["mobility"],
    summary="Universities for student",
    description="Return the list of partner universities with the number of places for the student",
    response_model=None,
)
def list_universities_etudiant(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                        SELECT u.*, pl.number_of_places, pl.annee, CASE WHEN pl.annee = 4 THEN 8
                            ELSE 9 END as id_semestre
                        FROM MOB_partner_university_places pl
                        JOIN MOB_partner_university u
                            ON u.id_partner_university = pl.id_partner_university
                        WHERE pl.id_filiere = (
                            SELECT p.id_filiere
                            FROM LNM_etudiant e
                            JOIN LNM_promo p ON e.id_promo = p.id_promo
                            WHERE e.id_etudiant = %(id_etudiant)s
                        )
                        UNION
                        SELECT u.*, 999 as number_of_places,
                               (SELECT p.annee FROM LNM_etudiant e JOIN LNM_promo p
                                   ON e.id_promo = p.id_promo
                                   WHERE e.id_etudiant = %(id_etudiant)s) as annee,
                               CASE WHEN (SELECT p.annee FROM LNM_etudiant e JOIN LNM_promo p
                                   ON e.id_promo = p.id_promo
                                   WHERE e.id_etudiant = %(id_etudiant)s) = 4 THEN 8 ELSE 9
                                   END as id_semestre
                        FROM MOB_partner_university u
                        WHERE u.type = 'stage'
                    """,
        "params": {"id_etudiant": id_etudiant},
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    # if(current_user.id == id_etudiant):
    #    request["allowedRolesRequester"] += [current_user.ExplicitSecondaryK]
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/university/admin/catalog",
    tags=["mobility"],
    summary="University catalog for RI",
    description=(
        "Return partner universities enriched with their available filieres for "
        "International Relations admins"
    ),
    response_model=None,
)
def list_university_catalog_ri(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    request_catalog = {
        "request": """
                        SELECT
                            u.*,
                            pl.number_of_places,
                            pl.annee,
                            pl.id_filiere,
                            f.nom_filiere,
                            f.nom_long
                        FROM MOB_partner_university u
                        LEFT JOIN MOB_partner_university_places pl
                            ON u.id_partner_university = pl.id_partner_university
                        LEFT JOIN LNM_filiere f ON f.id_filiere = pl.id_filiere
                        ORDER BY u.name ASC, f.nom_filiere ASC, pl.annee ASC
                    """,
        "allowedRolesRequester": ["connected_user"],
    }
    universities = db_request(current_user, SQLRequest(**request_catalog))

    request_semesters = {
        "request": """
                        SELECT DISTINCT
                            annee AS id,
                            CASE WHEN annee = 4 THEN 'S8' ELSE 'S9' END AS label
                        FROM LNM_promo
                        WHERE annee IN (4, 5)
                        ORDER BY annee ASC
                    """,
        "allowedRolesRequester": ["connected_user"],
    }
    semesters = db_request(current_user, SQLRequest(**request_semesters))

    if not semesters:
        semesters = [{"id": 4, "label": "S8"}, {"id": 5, "label": "S9"}]

    return {"universities": universities if universities else [], "semesters": semesters}
