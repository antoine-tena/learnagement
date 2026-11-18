from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.get(
    "/m2c3",
    tags=["module"],
    summary="M2c3",
    description="Return maquette et modalités de contrôle de connaissances et compétences",
    response_model=None,
)
def get_m2c3(
    current_user: Annotated[User, Depends(get_current_active_user)], id_filiere: int, id_statut: int
) -> Rows:
    request = {
        # ToDo convert parameters to be SQLAlchemy Core compatible when it is up
        "request": """SELECT MAQUETTE_module.id_module,
                            MAQUETTE_module.code_module,
                            MAQUETTE_module.nom,
                            CAST(MAQUETTE_module.ECTS AS FLOAT) AS ECTS,
                            MAQUETTE_module.hCM,
                            MAQUETTE_module.hTD,
                            MAQUETTE_module.hTP,
                            MAQUETTE_module.hPROJ,
                            MAQUETTE_module.hPersonnelle,
                            MAQUETTE_learning_unit.learning_unit_code,
                            LNM_filiere.nom_filiere,
                            LNM_promo.annee,
                            LNM_statut.nom_statut,
                            ExplicitSecondaryKs_LNM_enseignant.ExplicitSecondaryK AS "Responsable"
                        FROM `MAQUETTE_module`
                        JOIN MAQUETTE_module_as_learning_unit
                            ON MAQUETTE_module_as_learning_unit.id_module
                                = MAQUETTE_module.id_module
                        JOIN MAQUETTE_learning_unit
                            ON MAQUETTE_learning_unit.id_learning_unit
                                = MAQUETTE_module_as_learning_unit.id_learning_unit
                        JOIN LNM_promo ON LNM_promo.id_promo = MAQUETTE_learning_unit.id_promo
                        JOIN LNM_filiere ON LNM_filiere.id_filiere = LNM_promo.id_filiere
                        JOIN LNM_statut ON LNM_statut.id_statut = LNM_promo.id_statut
                        JOIN ExplicitSecondaryKs_LNM_enseignant
                            ON ExplicitSecondaryKs_LNM_enseignant.id_enseignant
                                = MAQUETTE_module.id_responsable
                        WHERE LNM_filiere.id_filiere = %(id_filiere)s
                            AND LNM_statut.id_statut= %(id_statut)s;
                """,
        "params": {
            "id_filiere": id_filiere,
            "id_statut": id_statut,
        },
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/modules/responsables",
    tags=["module"],
    summary="Get responsibles",
    description="Get modules responsibles",
    response_model=None,
)
def get_modules_responsables(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                SELECT
                    MAQUETTE_module.id_module,
                    MAQUETTE_module.code_module,
                    MAQUETTE_module.nom as nom_module,
                    LNM_semestre.semestre,
                    MAQUETTE_module.hCM,
                    MAQUETTE_module.hTD,
                    MAQUETTE_module.hTP,
                    MAQUETTE_module.hPROJ,
                    MAQUETTE_module.hPersonnelle,
                    MAQUETTE_module.commentaire,
                    LNM_enseignant.nom,
                    LNM_enseignant.prenom
                FROM `MAQUETTE_module`
                    LEFT JOIN LNM_semestre ON LNM_semestre.id_semestre = MAQUETTE_module.id_semestre
                    LEFT JOIN MAQUETTE_module_sequencage
                        ON MAQUETTE_module_sequencage.id_module = MAQUETTE_module.id_module
                    LEFT JOIN MAQUETTE_module_sequence
                        ON MAQUETTE_module_sequence.id_module_sequencage
                            = MAQUETTE_module_sequencage.id_module_sequencage
                    LEFT JOIN CLASS_session
                        ON CLASS_session.id_module_sequence
                            = MAQUETTE_module_sequence.id_module_sequence
                    LEFT JOIN LNM_enseignant
                        ON LNM_enseignant.id_enseignant = CLASS_session.id_enseignant""",
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/modules/responsables/{id_responsable}",
    tags=["module"],
    summary="Get modules by responsible",
    description="Get all modules of a responsible",
    response_model=None,
)
def get_modules_responsable(
    id_responsable: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                SELECT
                    MAQUETTE_module.id_module,
                    MAQUETTE_module.code_module,
                    MAQUETTE_module.nom as nom_module,
                    LNM_semestre.semestre,
                    MAQUETTE_module.hCM,
                    MAQUETTE_module.hTD,
                    MAQUETTE_module.hTP,
                    MAQUETTE_module.hPROJ,
                    MAQUETTE_module.hPersonnelle,
                    MAQUETTE_module.commentaire,
                    LNM_enseignant.nom,
                    LNM_enseignant.prenom
                FROM `MAQUETTE_module`
                    LEFT JOIN LNM_semestre ON LNM_semestre.id_semestre = MAQUETTE_module.id_semestre
                    LEFT JOIN MAQUETTE_module_sequencage
                        ON MAQUETTE_module_sequencage.id_module = MAQUETTE_module.id_module
                    LEFT JOIN MAQUETTE_module_sequence
                        ON MAQUETTE_module_sequence.id_module_sequencage
                            = MAQUETTE_module_sequencage.id_module_sequencage
                    LEFT JOIN CLASS_session
                        ON CLASS_session.id_module_sequence
                            = MAQUETTE_module_sequence.id_module_sequence
                    LEFT JOIN LNM_enseignant
                        ON LNM_enseignant.id_enseignant = CLASS_session.id_enseignant
                WHERE `id_responsable` = %(id_responsable)s""",
        "params": {
            "id_responsable": id_responsable,
        },
        "allowedRolesRequester": {
            "roles": ["enseignant", "administratif"],
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/modules/etudiants/{id_etudiant}",
    tags=["module"],
    summary="Get modules by responsible",
    description="Get all modules of a responsible",
    response_model=None,
)
def get_modules_etudiant(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT MAQUETTE_module.id_module,
                MAQUETTE_module.code_module,
                MAQUETTE_module.nom
            FROM `MAQUETTE_module`
                JOIN MAQUETTE_module_as_learning_unit
                    ON MAQUETTE_module_as_learning_unit.id_module = MAQUETTE_module.id_module
                JOIN MAQUETTE_learning_unit
                    ON MAQUETTE_learning_unit.id_learning_unit
                        = MAQUETTE_module_as_learning_unit.id_learning_unit
                JOIN LNM_promo ON LNM_promo.id_promo = MAQUETTE_learning_unit.id_promo
                JOIN LNM_etudiant ON LNM_etudiant.id_promo = LNM_promo.id_promo
            WHERE LNM_etudiant.id_etudiant = %(id_etudiant)s
        """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/disciplines",
    tags=["module"],
    summary="Get disciplines",
    description="Get disciplines",
    response_model=None,
)
def get_disciplines(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                SELECT
                    *
                FROM `MAQUETTE_discipline`""",
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/module/{id_module}/apc",
    tags=["module"],
    summary="Get APC of a module",
    description="Get APC of a module",
    response_model=None,
)
def get_module_apc(
    id_module: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                SELECT
                    `APC_apprentissage_critique_as_module`.`id_apprentissage_critique`,
                    `APC_apprentissage_critique`.`libelle_apprentissage`
                FROM `APC_apprentissage_critique_as_module`
                JOIN `APC_apprentissage_critique`
                    ON `APC_apprentissage_critique_as_module`.`id_apprentissage_critique`
                        = `APC_apprentissage_critique`.`id_apprentissage_critique`
                WHERE `APC_apprentissage_critique_as_module`.`id_module` = %(id_module)s;
            """,
        "params": {"id_module": id_module},
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))
