from typing import Annotated, Any

from fastapi import APIRouter, Depends

from api.dependencies import Rows, db_request, get_current_active_user
from models.request import SQLRequest
from models.user import User

router = APIRouter()


@router.get(
    "/etudiants/stages",
    tags=[
        "administratif",
        "student",
        "internship",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiants_stages(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT
                LNM_stage.id_stage,
                LNM_stage.`entreprise`,
                LNM_stage.`intitulé`,
                LNM_stage.`description`,
                LNM_stage.`ville`,
                DATE_FORMAT(LNM_stage.`date_debut`, '%Y-%m-%d') AS date_debut,
                DATE_FORMAT(LNM_stage.`date_fin`, '%Y-%m-%d') AS date_fin,
                LNM_stage.`nature`,
                ExplicitSecondaryKs_LNM_etudiant.ExplicitSecondaryK AS student_fullname,
                LNM_etudiant.mail,
                LNM_etudiant.id_etudiant,
                ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK AS filiere,
                ExplicitSecondaryKs_LNM_enseignant.ExplicitSecondaryK AS teacher_fullname,
                LNM_enseignant.id_enseignant,
                LNM_enseignant.mail AS teacher_mail,
                CASE
                    WHEN LNM_stage.id_stage IS NULL THEN 'no-internship'
                    WHEN LNM_enseignant.id_enseignant IS NULL THEN 'pending'
                    ELSE 'completed'
                END AS status
            FROM LNM_etudiant
            JOIN ExplicitSecondaryKs_LNM_etudiant
                ON ExplicitSecondaryKs_LNM_etudiant.id_etudiant = LNM_etudiant.id_etudiant
            JOIN LNM_promo ON LNM_promo.id_promo = LNM_etudiant.id_promo
            JOIN LNM_filiere ON LNM_filiere.id_filiere = LNM_promo.id_filiere
            JOIN ExplicitSecondaryKs_LNM_promo
                ON ExplicitSecondaryKs_LNM_promo.id_promo = LNM_promo.id_promo
            LEFT JOIN LNM_stage ON LNM_stage.id_etudiant = LNM_etudiant.id_etudiant
            LEFT JOIN LNM_enseignant ON LNM_enseignant.id_enseignant = LNM_stage.id_enseignant
            LEFT JOIN ExplicitSecondaryKs_LNM_enseignant
                ON ExplicitSecondaryKs_LNM_enseignant.id_enseignant = LNM_enseignant.id_enseignant;
                    """,
        "allowedRolesRequester": ["responsable_etudes", "responsable_stages", "enseignant"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/etudiants/without_stage",
    tags=["administratif", "student", "internship"],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiants_without_stage(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT `LNM_etudiant`.`id_etudiant`,
                   `LNM_etudiant`.`nom`,
                   `LNM_etudiant`.`prenom`,
                   ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK AS "promo"
            FROM `LNM_etudiant`
                     JOIN ExplicitSecondaryKs_LNM_promo
                         ON ExplicitSecondaryKs_LNM_promo.id_promo = LNM_etudiant.id_promo
            WHERE `LNM_etudiant`.`id_etudiant`
                      NOT IN ( SELECT `LNM_stage`.`id_etudiant` FROM `LNM_stage` WHERE 1)
                    """,
        "allowedRolesRequester": ["responsable_etudes", "responsable_stages"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/etudiants/{id_etudiant:int}/stages",
    tags=[
        "administratif",
        "student",
        "internship",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def get_etudiant_stages(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT LNM_stage.`id_stage`,
                   ExplicitSecondaryKs_LNM_etudiant.ExplicitSecondaryK AS "étudiant",
                   ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK AS "promo",
                   LNM_stage.`entreprise`,
                   LNM_stage.`intitulé`,
                   LNM_stage.`description`,
                   LNM_stage.`ville`,
                   DATE_FORMAT(LNM_stage.`date_debut`, '%Y-%m-%d') AS date_debut,
                   DATE_FORMAT(LNM_stage.`date_fin`, '%Y-%m-%d') AS date_fin,
                   LNM_stage.`nature`,
                   ExplicitSecondaryKs_LNM_enseignant.ExplicitSecondaryK AS "enseignant"
            FROM `LNM_stage`
                     JOIN LNM_etudiant ON LNM_etudiant.id_etudiant = LNM_stage.id_etudiant
                     LEFT JOIN LNM_enseignant
                         ON LNM_enseignant.id_enseignant = LNM_stage.id_enseignant
                     JOIN ExplicitSecondaryKs_LNM_promo
                         ON ExplicitSecondaryKs_LNM_promo.id_promo = LNM_etudiant.id_promo
                     JOIN ExplicitSecondaryKs_LNM_etudiant
                         ON ExplicitSecondaryKs_LNM_etudiant.id_etudiant = LNM_etudiant.id_etudiant
                     LEFT JOIN ExplicitSecondaryKs_LNM_enseignant
                         ON ExplicitSecondaryKs_LNM_enseignant.id_enseignant
                             = LNM_enseignant.id_enseignant
            WHERE LNM_stage.id_etudiant = %(id_etudiant)s;
                    """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": {
            "roles": ["responsable_etudes", "responsable_stages"],
            "owner": {"role": "etudiant", "id": "id_etudiant"},
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.post(
    "/etudiants/{id_etudiant:int}/stage",
    tags=[
        "administratif",
        "student",
        "internship",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def post_etudiant_stage(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: dict[str, Any],
) -> Rows:
    # ToDo convert parameters to be SQLAlchemy Core compatible when it will be up
    if "id_enseignant" not in data or not data["id_enseignant"]:
        data["id_enseignant"] = "null"
        request = {
            "request": """
                        INSERT INTO `LNM_stage` (`entreprise`, `intitulé`, `description`, `ville`,
                            `date_debut`, `date_fin`, `nature`, `id_etudiant`)
                        VALUES (%(entreprise)s, %(intitule)s, %(description)s, %(ville)s,
                            %(date_debut)s, %(date_fin)s, %(nature)s, %(id_etudiant)s)
            """,
        }
    else:
        request = {
            "request": """
                        INSERT INTO `LNM_stage` (`entreprise`, `intitulé`, `description`, `ville`,
                            `date_debut`, `date_fin`, `nature`, `id_etudiant`, `id_enseignant`)
                        VALUES (%(entreprise)s, %(intitule)s, %(description)s, %(ville)s,
                            %(date_debut)s, %(date_fin)s, %(nature)s, %(id_etudiant)s,
                            %(id_enseignant)s)
            """,
        }
    request.update(
        {
            "params": {
                "entreprise": data["entreprise"],
                "intitule": data["intitule"],
                "description": data["description"],
                "ville": data["ville"],
                "date_debut": data["date_debut"],
                "date_fin": data["date_fin"],
                "nature": data["nature"],
                "id_etudiant": id_etudiant,
                "id_enseignant": data["id_enseignant"],
            },
            "allowedRolesRequester": ["responsable_stages"],
        }
    )
    return db_request(current_user, SQLRequest(**request))


@router.patch(
    "/etudiants/{id_etudiant:int}/stages/{id_stage:int}",
    tags=[
        "administratif",
        "student",
        "internship",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def patch_etudiant_stage(
    id_etudiant: int,
    id_stage: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
    data: dict[str, Any],
) -> Rows:
    # ToDo il pourrait être intéressant de vérifier que le stage est bien à l'étudiant
    # ToDo convert parameters to be SQLAlchemy Core compatible when it will be up
    request = {
        "request": """
                    UPDATE LNM_stage
                    SET id_enseignant = %(id_enseignant)s
                    WHERE id_stage = %(id_stage)s
        """,
        "params": {
            "id_enseignant": data["id_enseignant"],
            "id_stage": id_stage,
        },
        "allowedRolesRequester": ["responsable_stages"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.delete(
    "/etudiants/{id_etudiant:int}/stages/{id_stage:int}",
    tags=[
        "administratif",
        "student",
        "internship",
    ],
    summary="Students",
    description="Return the list of students",
    response_model=None,
)
def delete_etudiant_stage(
    id_etudiant: int,
    id_stage: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    # ToDo il pourrait être intéressant de vérifier que le stage est bien à l'étudiant
    # ToDo convert parameters to be SQLAlchemy Core compatible when it will be up
    request = {
        "request": """
                   DELETE FROM `LNM_stage` WHERE `id_stage`= %(id_stage)s
                   """,
        "params": {
            "id_stage": id_stage,
        },
        "allowedRolesRequester": ["responsable_stages"],
    }
    return db_request(current_user, SQLRequest(**request))
