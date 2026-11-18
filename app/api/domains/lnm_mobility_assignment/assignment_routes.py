"""Routes d'exécution et de suivi de l'algorithme d'affectation mobilité."""

import time
from typing import Annotated

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from api.dependencies import get_current_active_user
from models.user import User

from .algorithm import run_round_robin_assignment
from .queries import (
    get_available_places,
    get_eligible_students,
    get_mobility_quotas_from_db,
    get_student_wishes,
    save_assignments,
    sort_students_by_z_score,
)
from .schemas import AssignmentRunPayload

# FixMe global variable that store app data must be store in data area (BD or other) not in API
# backend
assignment_progress = {"is_running": False, "progress": 0, "step": "", "error": None}

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get(
    "/university/admin/assignment/status",
    tags=["admin", "mobility"],
    summary="Get assignment progress",
    response_model=None,
)
def get_assignment_status(
    current_user: Annotated[User, Depends(get_current_active_user)],  # to require connected user
) -> object:
    return assignment_progress


def execute_assignment_task(payload: AssignmentRunPayload, current_user: User) -> None:
    global assignment_progress
    assignment_progress = {"is_running": True, "progress": 0, "step": "Démarrage...", "error": None}
    try:
        time.sleep(0.5)
        assignment_progress["progress"] = 10
        assignment_progress["step"] = "Étape 1 : Récupération des étudiants éligibles..."
        students = get_eligible_students(current_user=current_user)

        time.sleep(0.5)
        assignment_progress["progress"] = 30
        assignment_progress["step"] = "Étape 2 : Tri des étudiants..."
        sorted_students = sort_students_by_z_score(students)

        time.sleep(0.5)
        assignment_progress["progress"] = 50
        assignment_progress["step"] = "Étape 3 : Récupération des vœux et places disponibles..."
        wishes = get_student_wishes(current_user)
        places = get_available_places(current_user)

        time.sleep(0.5)
        assignment_progress["progress"] = 70
        assignment_progress["step"] = "Étape 4 : Exécution de l'algorithme Round-Robin..."

        # Récupération des quotas persistés depuis la base de données
        quotas_from_db = get_mobility_quotas_from_db(payload.annee_scolaire, current_user)
        # S'ils sont vides, on utilise ceux du payload en fallback
        active_quotas = quotas_from_db if quotas_from_db else payload.mobility_quotas

        result = run_round_robin_assignment(sorted_students, wishes, places, active_quotas)
        assignments = result["assignments"]
        final_places = result["final_places"]

        time.sleep(0.5)
        assignment_progress["progress"] = 90
        assignment_progress["step"] = "Étape 5 : Sauvegarde des affectations..."
        save_assignments(assignments, final_places, current_user)

        time.sleep(0.5)
        assignment_progress["progress"] = 100
        assignment_progress["step"] = "Terminé !"
        assignment_progress["is_running"] = False
    except Exception as e:
        logger.exception("mobility.assignment_failed")
        assignment_progress["error"] = str(e)
        assignment_progress["is_running"] = False


@router.post(
    "/university/admin/assignment/run",
    tags=["admin", "mobility"],
    summary="Run assignment algorithm",
    description="Lancer l'algorithme d'affectation automatique pour la mobilité internationale",
    response_model=None,
)
def run_mobility_assignment(
    payload: AssignmentRunPayload,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    """
    Route principale de l'algorithme (asynchrone).
    Seuls les administrateurs RI pourront lancer cette route.
    """
    if assignment_progress["is_running"]:
        raise HTTPException(status_code=400, detail="Une affectation est déjà en cours.")

    background_tasks.add_task(execute_assignment_task, payload, current_user)
    return {"message": "Algorithme d'affectation démarré en arrière-plan."}
