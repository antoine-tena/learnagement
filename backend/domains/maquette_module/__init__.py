import structlog
from fastapi import APIRouter

from api.dependencies import db_request

from .dependencies_gantt import (
    get_data_gantt_endpoint,
    get_data_gantt_endpoint_etudiant,
    get_module_dependencies,
    get_module_sequence_dependencies,
)
from .dependencies_gantt import (
    router as dependencies_gantt_router,
)
from .intervenants import (
    get_modules_intervenant,
    get_modules_intervenants,
)
from .intervenants import (
    router as intervenants_router,
)
from .mutations import (
    add_dependencies,
    add_sequencage,
    delete_dependencies,
    delete_sequencage,
)
from .mutations import (
    router as mutations_router,
)
from .overview import (
    get_disciplines,
    get_m2c3,
    get_module_apc,
    get_modules_etudiant,
    get_modules_responsable,
    get_modules_responsables,
)
from .overview import (
    router as overview_router,
)
from .sequencing_read import (
    get_sequencages_responsable,
    get_sequences_responsable,
    get_sessions_responsable,
)
from .sequencing_read import (
    router as sequencing_read_router,
)
from .updates import (
    router as updates_router,
)
from .updates import (
    update_module,
    update_sequencage,
    update_sequence,
    update_session,
)

logger = structlog.get_logger(__name__)

router = APIRouter()
router.include_router(overview_router)
router.include_router(intervenants_router)
router.include_router(sequencing_read_router)
router.include_router(dependencies_gantt_router)
router.include_router(updates_router)
router.include_router(mutations_router)

__all__ = [
    "add_dependencies",
    "add_sequencage",
    "db_request",
    "delete_dependencies",
    "delete_sequencage",
    "get_data_gantt_endpoint",
    "get_data_gantt_endpoint_etudiant",
    "get_disciplines",
    "get_m2c3",
    "get_module_apc",
    "get_module_dependencies",
    "get_module_sequence_dependencies",
    "get_modules_etudiant",
    "get_modules_intervenant",
    "get_modules_intervenants",
    "get_modules_responsable",
    "get_modules_responsables",
    "get_sequencages_responsable",
    "get_sequences_responsable",
    "get_sessions_responsable",
    "logger",
    "router",
    "update_module",
    "update_sequencage",
    "update_sequence",
    "update_session",
]
