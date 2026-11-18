"""Routes FastAPI pour les arbres de compétences APC."""

from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.get(
    "/competence",
    tags=["competence"],
    summary="Universities",
    description="Return the list of partner universities",
    response_model=None,
)
def tree_competence(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                        SELECT APC_competence.code_competence,
                               APC_competence.libelle_competence,
        CONCAT(APC_competence.code_competence,"_N",APC_niveau.niveau) AS 'code_niveau',
                               APC_niveau.niveau,
                               CONCAT(APC_competence.code_competence,"_N",
        APC_niveau.niveau,"_AC",APC_apprentissage_critique.id_apprentissage_critique)  AS 'code_ac',
                               APC_apprentissage_critique.libelle_apprentissage,
                                   MAQUETTE_module.code_module, MAQUETTE_module.nom,
                               CAST(MAQUETTE_module.ECTS AS DOUBLE) AS 'ects',
                               IFNULL(MAQUETTE_module.hCM,0) AS 'hCM',
                               IFNULL(MAQUETTE_module.hTD,0) AS 'hTD',
                               IFNULL(MAQUETTE_module.hTP,0) AS 'hTP',
                               IFNULL(MAQUETTE_module.hPROJ,0)
                        FROM `APC_competence`
                        JOIN APC_niveau ON APC_niveau.id_competence = APC_competence.id_competence
                        JOIN APC_apprentissage_critique
                            ON APC_apprentissage_critique.id_niveau = APC_niveau.id_niveau
                        JOIN APC_apprentissage_critique_as_module
                            ON APC_apprentissage_critique_as_module.id_apprentissage_critique
                                = APC_apprentissage_critique.id_apprentissage_critique
                        JOIN MAQUETTE_module
                            ON MAQUETTE_module.id_module
                                = APC_apprentissage_critique_as_module.id_module
                        WHERE 1;
                    """,
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/competence_big",
    tags=["competence"],
    summary="Universities",
    description="Return the list of partner universities",
    response_model=None,
)
def tree_competence_big(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                   SELECT APC_competence.code_competence,
                               APC_competence.`id_competence`,
                               APC_competence.libelle_competence,
                               APC_competence.code_competence,
                               CONCAT(APC_competence.code_competence, "_CE",
        APC_composante_essentielle.id_composante_essentielle) AS 'code_ce',
                               APC_composante_essentielle.libelle_composante_essentielle,
        CONCAT(APC_competence.code_competence,"_N",APC_niveau.niveau) AS 'code_niveau',
                               APC_niveau.niveau,
                               CONCAT(APC_competence.code_competence,"_N",
        APC_niveau.niveau,"_AC",APC_apprentissage_critique.id_apprentissage_critique)  AS 'code_ac',
                               APC_apprentissage_critique.libelle_apprentissage,
                               MAQUETTE_module.code_module,
                               MAQUETTE_module.nom,
                               CAST(MAQUETTE_module.ECTS AS DOUBLE) AS 'ects',
                               IFNULL(MAQUETTE_module.hCM,0) AS 'hCM',
                               IFNULL(MAQUETTE_module.hTD,0) AS 'hTD',
                               IFNULL(MAQUETTE_module.hTP,0) AS 'hTP',
                               IFNULL(MAQUETTE_module.hPROJ,0),
                               MAQUETTE_learning_unit.learning_unit_code,
                               MAQUETTE_learning_unit.learning_unit_name,
                               LNM_filiere.nom_filiere,
                               LNM_statut.nom_statut,
                               LNM_promo.annee
                        FROM `APC_competence`
                        JOIN APC_composante_essentielle
          ON APC_composante_essentielle.id_competence = APC_competence.id_competence
                        JOIN APC_niveau ON APC_niveau.id_competence = APC_competence.id_competence
                        JOIN APC_apprentissage_critique
                            ON APC_apprentissage_critique.id_niveau = APC_niveau.id_niveau
                        JOIN APC_apprentissage_critique_as_module
                            ON APC_apprentissage_critique_as_module.id_apprentissage_critique
                                = APC_apprentissage_critique.id_apprentissage_critique
                        JOIN MAQUETTE_module
                            ON MAQUETTE_module.id_module
                                = APC_apprentissage_critique_as_module.id_module
                        JOIN MAQUETTE_module_as_learning_unit
                            ON MAQUETTE_module_as_learning_unit.id_module
                                = MAQUETTE_module.id_module
                        JOIN MAQUETTE_learning_unit
                            ON MAQUETTE_learning_unit.id_learning_unit
                                = MAQUETTE_module_as_learning_unit.id_learning_unit
                        JOIN LNM_promo ON LNM_promo.id_promo=MAQUETTE_learning_unit.id_promo
                        JOIN LNM_filiere ON LNM_filiere.id_filiere=LNM_promo.id_filiere
                        JOIN LNM_statut ON LNM_statut.id_statut=LNM_promo.id_statut
                        WHERE 1;
                    """,
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))
