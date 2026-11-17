"""Paquet d'affectation de mobilité internationale."""

from fastapi import APIRouter

from api.dependencies import db_request
from db.connection import get_connection

from .algorithm import run_round_robin_assignment
from .assignment_routes import (
    assignment_progress,
    execute_assignment_task,
    get_assignment_status,
    run_mobility_assignment,
)
from .assignment_routes import router as _assignment_router
from .queries import (
    get_available_places,
    get_eligible_students,
    get_mobility_quotas_from_db,
    get_student_wishes,
    save_assignments,
    sort_students_by_z_score,
)
from .quotas_routes import get_mobility_quotas, get_student_quota, save_mobility_quotas
from .quotas_routes import router as _quotas_router
from .schemas import AssignmentRunPayload, MobilityQuota, MobilityQuotasUpdatePayload

router = APIRouter()
router.include_router(_assignment_router)
router.include_router(_quotas_router)

__all__ = [
    "AssignmentRunPayload",
    "MobilityQuota",
    "MobilityQuotasUpdatePayload",
    "assignment_progress",
    "db_request",
    "execute_assignment_task",
    "get_assignment_status",
    "get_available_places",
    "get_connection",
    "get_eligible_students",
    "get_mobility_quotas",
    "get_mobility_quotas_from_db",
    "get_student_quota",
    "get_student_wishes",
    "router",
    "run_mobility_assignment",
    "run_round_robin_assignment",
    "save_assignments",
    "save_mobility_quotas",
    "sort_students_by_z_score",
]
