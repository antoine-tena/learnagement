"""Paquet des routes de compétences APC et d'évaluations."""

from fastapi import APIRouter

from api.dependencies import db_request

from .competence import router as _competence_router
from .competence import tree_competence, tree_competence_big
from .evaluations import (
    get_apc_etudiant_evaluation,
    get_classical_etudiant_evaluation,
    get_classical_evaluations_enseignant,
    get_classical_module_evaluation,
    get_classical_module_evaluation_average,
)
from .evaluations import router as _evaluations_router

router = APIRouter()
router.include_router(_competence_router)
router.include_router(_evaluations_router)

__all__ = [
    "db_request",
    "get_apc_etudiant_evaluation",
    "get_classical_etudiant_evaluation",
    "get_classical_evaluations_enseignant",
    "get_classical_module_evaluation",
    "get_classical_module_evaluation_average",
    "router",
    "tree_competence",
    "tree_competence_big",
]
