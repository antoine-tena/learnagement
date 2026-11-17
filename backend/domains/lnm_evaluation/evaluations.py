"""Routes FastAPI pour les évaluations APC et classiques."""

from typing import Annotated

from fastapi import APIRouter, Depends

from access_control.predicates import is_current_user_module_participant
from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.get(
    "/evaluations/apc/etudiants/{id_etudiant}",
    tags=["student"],
    summary="Universities",
    description="Return the list of partner universities",
    response_model=None,
)
def get_apc_etudiant_evaluation(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                   SELECT eval.id_etudiant,
                           eval.evaluation,
                           ac.libelle_apprentissage,
                           niveau.libelle_niveau,
                           competence.libelle_competence,
                           competence.id_competence
                   FROM ETU_competence_evaluation as eval
                        INNER JOIN APC_apprentissage_critique as ac
                            ON eval.id_apprentissage_critique=ac.id_apprentissage_critique
                        INNER JOIN APC_niveau as niveau ON ac.id_niveau=niveau.id_niveau
                        INNER JOIN APC_competence as competence
                            ON niveau.id_competence=competence.id_competence
                   WHERE eval.id_etudiant = %(id_etudiant)s
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
    "/evaluations/classical/etudiants/{id_etudiant}",
    tags=["student"],
    summary="Universities",
    description="Return the list of partner universities",
    response_model=None,
)
def get_classical_etudiant_evaluation(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                   SELECT CAST(evaluation AS FLOAT) AS evaluation,
                          module.id_module,
                          module.code_module,
                          module.nom,
                          DATE_FORMAT(date , '%Y-%m-%dT%H:%i') AS 'date'
                   FROM ETU_classical_evaluation as eval
                       JOIN MAQUETTE_module as module ON eval.id_module=module.id_module
                   WHERE eval.id_etudiant=%(id_etudiant)s
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
    "/evaluations/classical/modules/{id_module}",
    tags=["student"],
    summary="Universities",
    description="Return the list of partner universities",
    response_model=None,
)
def get_classical_module_evaluation(
    id_module: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                   SELECT CAST(evaluation AS FLOAT) AS evaluation,
                          module.nom,
                          DATE_FORMAT(date , '%Y-%m-%dT%H:%i') AS 'date'
                   FROM ETU_classical_evaluation as eval
                       JOIN MAQUETTE_module as module ON eval.id_module=module.id_module
                   WHERE eval.id_module=%(id_module)s
                   """,
        "params": {
            "id_module": id_module,
        },
        "allowedRolesRequester": {
            "roles": [],
            "predicate": is_current_user_module_participant,
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/evaluations/classical/modules/{id_module}/average",
    tags=["student"],
    summary="Universities",
    description="Return the list of partner universities",
    response_model=None,
)
def get_classical_module_evaluation_average(
    id_module: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                   SELECT CAST(AVG(evaluation) AS FLOAT)  AS 'evaluation'
                   FROM ETU_classical_evaluation AS eval
                            JOIN MAQUETTE_module AS module ON eval.id_module=module.id_module
                   WHERE eval.id_module=%(id_module)s
                   GROUP BY eval.id_etudiant
                   """,
        "params": {
            "id_module": id_module,
        },
        "allowedRolesRequester": {
            "roles": [],
            "predicate": is_current_user_module_participant,
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/evaluations/classical/enseignants/{id_enseignant}",
    tags=["enseignant"],
    summary="Universities",
    description="Return the list of partner universities",
    response_model=None,
)
def get_classical_evaluations_enseignant(
    id_enseignant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
                   SELECT ETU_classical_evaluation.evaluation,
                          concat(LNM_etudiant.nom, ' ', LNM_etudiant.prenom) as etudiant,
                          MAQUETTE_module.nom,
                          DATE_FORMAT(ETU_classical_evaluation.date , '%Y-%m-%dT%H:%i') AS 'date'  ,
                          concat(LNM_filiere.nom_filiere, '_', LNM_promo.annee, '_',
                              LNM_statut.nom_statut) AS 'promo'
                   FROM ETU_classical_evaluation
                            JOIN MAQUETTE_module
                                ON ETU_classical_evaluation.id_module = MAQUETTE_module.id_module
                            JOIN LNM_enseignant
                                ON MAQUETTE_module.id_responsable = LNM_enseignant.id_enseignant
                            JOIN LNM_etudiant
                                ON LNM_etudiant.id_etudiant = ETU_classical_evaluation.id_etudiant
                            JOIN LNM_promo ON LNM_etudiant.id_promo = LNM_promo.id_promo
                            JOIN LNM_filiere ON LNM_filiere.id_filiere = LNM_promo.id_filiere
                            JOIN LNM_statut ON LNM_statut.id_statut = LNM_promo.id_statut
                   WHERE LNM_enseignant.id_enseignant=%(id_enseignant)s
                   """,
        "params": {
            "id_enseignant": id_enseignant,
        },
        "allowedRolesRequester": {
            "roles": [],
            "owner": {"role": "enseignant", "id": "id_enseignant"},
        },
    }
    return db_request(current_user, SQLRequest(**request))
