import structlog
from fastapi import APIRouter

from api.dependencies import db_request

from .student_academic import (
    get_etudiant_edt,
    get_etudiant_load,
    get_etudiant_pastedt,
    get_etudiant_polypoints,
    get_etudiant_rendus,
)
from .student_academic import (
    router as student_academic_router,
)
from .student_internships import (
    delete_etudiant_stage,
    get_etudiant_stages,
    get_etudiants_stages,
    get_etudiants_without_stage,
    patch_etudiant_stage,
    post_etudiant_stage,
)
from .student_internships import (
    router as student_internships_router,
)
from .students_list import (
    AbsencesFilters,
    get_etudiant,
    get_etudiant_absences,
    get_etudiants,
    get_etudiants_absences,
)
from .students_list import (
    router as students_list_router,
)

logger = structlog.get_logger(__name__)

router = APIRouter()
router.include_router(students_list_router)
router.include_router(student_academic_router)
router.include_router(student_internships_router)

__all__ = [
    "AbsencesFilters",
    "db_request",
    "delete_etudiant_stage",
    "get_etudiant",
    "get_etudiant_absences",
    "get_etudiant_edt",
    "get_etudiant_load",
    "get_etudiant_pastedt",
    "get_etudiant_polypoints",
    "get_etudiant_rendus",
    "get_etudiant_stages",
    "get_etudiants",
    "get_etudiants_absences",
    "get_etudiants_stages",
    "get_etudiants_without_stage",
    "logger",
    "patch_etudiant_stage",
    "post_etudiant_stage",
    "router",
]
