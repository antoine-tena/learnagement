"""Routes de gestion des quotas de mobilité internationale."""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request, get_connection
from .schemas import MobilityQuotasUpdatePayload

router = APIRouter()


@router.get(
    "/university/admin/mobility-quotas",
    tags=["admin", "mobility"],
    summary="Get mobility quotas",
    description="Récupérer les quotas de mobilité par filière",
    response_model=None,
)
def get_mobility_quotas(
    annee_scolaire: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    query = """
        SELECT id_filiere, id_semestre, places
        FROM MOB_filiere_quotas
        WHERE annee_scolaire = %(annee_scolaire)s
    """
    sql_request = SQLRequest(
        request=query,
        params={"annee_scolaire": annee_scolaire},
        allowedRolesRequester=["relations_internationales"],
    )
    return db_request(current_user, sql_request)


@router.post(
    "/university/admin/mobility-quotas",
    tags=["admin", "mobility"],
    summary="Save mobility quotas",
    description="Sauvegarder les quotas de mobilité par filière",
    response_model=None,
)
def save_mobility_quotas(
    payload: MobilityQuotasUpdatePayload,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    allowed = ["relations_internationales"]
    with get_connection() as conn:
        # D'abord, supprimer les anciens quotas pour cette année
        delete_query = """
            DELETE FROM MOB_filiere_quotas
            WHERE annee_scolaire = %(annee_scolaire)s
        """
        sql_request = SQLRequest(
            request=delete_query,
            params={"annee_scolaire": payload.annee_scolaire},
            allowedRolesRequester=allowed,
        )
        db_request(current_user, sql_request, conn=conn)

        # Ensuite, insérer les nouveaux quotas
        insert_query = """
            INSERT INTO MOB_filiere_quotas (id_filiere, annee_scolaire, id_semestre, places)
            VALUES (%(id_filiere)s, %(annee_scolaire)s, %(id_semestre)s, %(places)s)
        """
        for quota in payload.quotas:
            params = {
                "id_filiere": quota.id_filiere,
                "annee_scolaire": payload.annee_scolaire,
                "id_semestre": quota.id_semestre,
                "places": quota.places,
            }
            sql_request = SQLRequest(
                request=insert_query, params=params, allowedRolesRequester=allowed
            )
            db_request(current_user, sql_request, conn=conn)

        return {"message": "Quotas sauvegardés avec succès."}


@router.get(
    "/university/etudiant/{id_etudiant}/quota",
    tags=["etudiant", "mobility"],
    summary="Get student mobility quota",
    description="Récupérer les quotas disponibles pour la filière d'un étudiant",
    response_model=None,
)
def get_student_quota(
    id_etudiant: int,
    annee_scolaire: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    # Récupérer la filière de l'étudiant
    # Note : allowedRolesRequester contient "connected_user" pour permettre à l'étudiant de
    # l'appeler.
    query = """
        SELECT q.id_semestre, q.places, f.nom_filiere
        FROM MOB_filiere_quotas q
        JOIN LNM_promo p ON p.id_filiere = q.id_filiere
        JOIN LNM_etudiant e ON e.id_promo = p.id_promo
        JOIN LNM_filiere f ON f.id_filiere = q.id_filiere
        WHERE e.id_etudiant = %(id_etudiant)s
          AND q.annee_scolaire = %(annee_scolaire)s
    """
    sql_request = SQLRequest(
        request=query,
        params={"id_etudiant": id_etudiant, "annee_scolaire": annee_scolaire},
        allowedRolesRequester=["connected_user"],
    )
    result = db_request(current_user, sql_request)

    if not result:
        return {"S8": 0, "S9": 0, "filiere": "Inconnue"}

    quotas_dict = {"S8": 0, "S9": 0, "filiere": result[0]["nom_filiere"]}
    for row in result:
        if row["id_semestre"] == 8:
            quotas_dict["S8"] = row["places"]
        elif row["id_semestre"] == 9:
            quotas_dict["S9"] = row["places"]

    return quotas_dict
