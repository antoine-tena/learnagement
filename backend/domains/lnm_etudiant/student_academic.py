from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import Rows, db_request, get_current_active_user
from models.request import SQLRequest
from models.user import User

router = APIRouter()


@router.get(
    "/etudiants/{id_etudiant:int}/load",
    tags=[
        "student",
        "administratif",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiant_load(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    # ToDo convert parameters to be SQLAlchemy Core compatible when it will be up
    request = {
        "request": """
                SELECT
                    DATE_FORMAT(session.schedule, '%Y-%m-%dT%H:%i') AS schedule,
                    CAST(sequencage.duree_h AS FLOAT) AS duree_h,
                    module.nom
                FROM CLASS_session as session
                    JOIN LNM_groupe as grp ON session.id_groupe = grp.id_groupe
                    JOIN LNM_promo as promo ON grp.id_promo = promo.id_promo
                    JOIN LNM_etudiant as etu ON grp.id_promo = etu.id_promo
                    JOIN MAQUETTE_module_sequence as sequence
                        ON session.id_module_sequence=sequence.id_module_sequence
                    JOIN MAQUETTE_module_sequencage as sequencage
                        ON sequence.id_module_sequencage=sequencage.id_module_sequencage
                    JOIN MAQUETTE_module as module ON sequencage.id_module=module.id_module
                WHERE etu.id_etudiant = %(id_etudiant)s
            """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": {
            "roles": ["administratif", "enseignant"],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/etudiants/{id_etudiant:int}/edt",
    tags=[
        "student",
        "administratif",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiant_edt(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    # ToDo convert parameters to be SQLAlchemy Core compatible when it will be up
    request = {
        "request": """
                    SELECT
                        etu.nom,
                        DATE_FORMAT(session.schedule, '%Y-%m-%dT%H:%i') AS date_prevue,
                        promo.annee,
                        CAST(sequencage.duree_h AS FLOAT) AS nb_heure,
                        module.nom AS matiere
                    FROM CLASS_session as session
                        JOIN LNM_groupe as grp ON session.id_groupe = grp.id_groupe
                        JOIN LNM_promo as promo ON grp.id_promo = promo.id_promo
                        JOIN LNM_etudiant as etu ON grp.id_promo = etu.id_promo
                        JOIN MAQUETTE_module_sequence as sequence
                            ON session.id_module_sequence=sequence.id_module_sequence
                        JOIN MAQUETTE_module_sequencage as sequencage
                            ON sequence.id_module_sequencage=sequencage.id_module_sequencage
                        JOIN MAQUETTE_module as module ON sequencage.id_module=module.id_module
                    WHERE etu.id_etudiant =   %(id_etudiant)s
                    ORDER BY session.schedule;
            """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": {
            "roles": [
                "administratif",
            ],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/etudiants/{id_etudiant:int}/pastedt",
    tags=[
        "student",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiant_pastedt(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    # ToDo convert parameters to be SQLAlchemy Core compatible when it will be up
    request = {
        "request": """
                    SELECT etu.nom,
                        DATE_FORMAT(session.schedule, '%Y-%m-%dT%H:%i') AS date_prevue,
                        promo.annee,
                        CAST(sequencage.duree_h AS FLOAT) AS nb_heure,
                        module.nom AS matiere
                    FROM CLASS_session as session
                        JOIN LNM_groupe as grp ON session.id_groupe = grp.id_groupe
                        JOIN LNM_promo as promo ON grp.id_promo = promo.id_promo
                        JOIN LNM_etudiant as etu ON grp.id_promo = etu.id_promo
                        JOIN MAQUETTE_module_sequence as sequence
                            ON session.id_module_sequence=sequence.id_module_sequence
                        JOIN MAQUETTE_module_sequencage as sequencage
                            ON sequence.id_module_sequencage=sequencage.id_module_sequencage
                        JOIN MAQUETTE_module as module ON sequencage.id_module=module.id_module
                    WHERE session.schedule < CURRENT_DATE
                        AND etu.id_etudiant = %(id_etudiant)s
                    ORDER BY session.schedule;
            """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/etudiants/{id_etudiant}/polypoints",
    tags=[
        "student",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiant_polypoints(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    # ToDo convert parameters to be SQLAlchemy Core compatible when it will be up
    request = {
        "request": """
            SELECT * FROM ETU_polypoint
            WHERE id_etudiant = %(id_etudiant)s
            ORDER BY annee_universitaire DESC;
            """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/etudiants/{id_etudiant}/rendus",
    tags=[
        "student",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiant_rendus(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    # ToDo convert parameters to be SQLAlchemy Core compatible when it will be up
    request = {
        "request": """
            SELECT rm.description,
            module.nom,
            ue.learning_unit_name,
            rm_etu.avancement,
            rm.date
            FROM LNM_rendu_module as rm
                JOIN LNM_rendu_module_as_etudiant as rm_etu
                    ON rm_etu.id_rendu_module=rm.id_rendu_module
                JOIN LNM_etudiant as etu ON etu.id_etudiant=rm_etu.id_etudiant
                JOIN MAQUETTE_module_as_learning_unit as mue ON rm.id_module=mue.id_module
                JOIN MAQUETTE_module as module ON mue.id_module=module.id_module
                JOIN MAQUETTE_learning_unit as ue ON mue.id_learning_unit=ue.id_learning_unit
            WHERE etu.id_etudiant = %(id_etudiant)s
            """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    return db_request(current_user, SQLRequest(**request))
