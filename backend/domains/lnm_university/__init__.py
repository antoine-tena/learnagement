import structlog
from fastapi import APIRouter

from api.dependencies import db_request

from .assignments import (
    get_assigned_students,
    get_student_assignment,
    submit_student_decision,
    sync_db_remaining_places,
    update_assignment_status,
)
from .assignments import (
    router as assignments_router,
)
from .campaign import (
    close_assignment_phase,
    get_mobility_diagnostics,
    launch_mobility_campaign,
    verify_doublant,
)
from .campaign import (
    router as campaign_router,
)
from .catalog import (
    list_universities,
    list_universities_etudiant,
    list_university_catalog_ri,
)
from .catalog import (
    router as catalog_router,
)
from .catalog_admin import (
    _sync_university_places,
    create_university_ri,
    update_university_ri,
)
from .catalog_admin import (
    router as catalog_admin_router,
)
from .exports_diagnostics import (
    export_mobility_diagnostics,
)
from .exports_diagnostics import (
    router as exports_diagnostics_router,
)
from .exports_places import (
    export_admin_places,
)
from .exports_places import (
    router as exports_places_router,
)
from .exports_status import (
    export_assigned_students_status,
    export_unassigned_students,
)
from .exports_status import (
    router as exports_status_router,
)
from .exports_wishes import (
    export_admin_assignments,
    export_admin_wishes,
)
from .exports_wishes import (
    router as exports_wishes_router,
)
from .schemas import (
    CampaignLaunchRequestPayload,
    DoublantScore,
    StudentDecisionPayload,
    UniversityAdminPayload,
    UniversityPlacePayload,
    UpdateAssignmentStatusPayload,
)
from .wishes import (
    add_university_to_wishes,
    get_campaign_status,
    list_university_wishes_etudiant,
)
from .wishes import (
    router as wishes_router,
)
from .wishes_manage import (
    delete_university_from_wishes,
    move_university_wish,
)
from .wishes_manage import (
    router as wishes_manage_router,
)
from .wishes_submission import (
    force_submit_wishes,
    get_submitted_students,
    list_all_wishes_ri,
    reset_student_wishes,
    submit_university_wishes,
)
from .wishes_submission import (
    router as wishes_submission_router,
)

logger = structlog.get_logger(__name__)

router = APIRouter()
router.include_router(catalog_router)
router.include_router(catalog_admin_router)
router.include_router(wishes_router)
router.include_router(wishes_manage_router)
router.include_router(wishes_submission_router)
router.include_router(assignments_router)
router.include_router(campaign_router)
router.include_router(exports_wishes_router)
router.include_router(exports_status_router)
router.include_router(exports_places_router)
router.include_router(exports_diagnostics_router)

__all__ = [
    "CampaignLaunchRequestPayload",
    "DoublantScore",
    "StudentDecisionPayload",
    "UniversityAdminPayload",
    "UniversityPlacePayload",
    "UpdateAssignmentStatusPayload",
    "_sync_university_places",
    "add_university_to_wishes",
    "close_assignment_phase",
    "create_university_ri",
    "db_request",
    "delete_university_from_wishes",
    "export_admin_assignments",
    "export_admin_places",
    "export_admin_wishes",
    "export_assigned_students_status",
    "export_mobility_diagnostics",
    "export_unassigned_students",
    "force_submit_wishes",
    "get_assigned_students",
    "get_campaign_status",
    "get_mobility_diagnostics",
    "get_student_assignment",
    "get_submitted_students",
    "launch_mobility_campaign",
    "list_all_wishes_ri",
    "list_universities",
    "list_universities_etudiant",
    "list_university_catalog_ri",
    "list_university_wishes_etudiant",
    "logger",
    "move_university_wish",
    "reset_student_wishes",
    "router",
    "submit_student_decision",
    "submit_university_wishes",
    "sync_db_remaining_places",
    "update_assignment_status",
    "update_university_ri",
    "verify_doublant",
]
