from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_current_active_user
from db.connection import get_connection
from models.request import SQLRequest
from models.user import User

from ._db import db_request
from .assignments import sync_db_remaining_places
from .schemas import CampaignLaunchRequestPayload

router = APIRouter()


@router.get(
    "/university/admin/mobility/diagnostics",
    tags=["admin", "mobility"],
    summary="Get statistics and diagnostics for mobility procedure",
    response_model=None,
)
def get_mobility_diagnostics(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    sql_request = SQLRequest(
        request="""
            SELECT
                e.id_etudiant,
                e.mobility_completed,
                (SELECT COUNT(w.id_partner_university) FROM MOB_wishes w
                    WHERE w.id_etudiant = e.id_etudiant) as wish_count,
                (SELECT MAX(w.submission_date) FROM MOB_wishes w
                    WHERE w.id_etudiant = e.id_etudiant) as last_submission_date
            FROM LNM_etudiant e
            JOIN LNM_promo p ON e.id_promo = p.id_promo
            WHERE p.annee = 4
        """,
        params=None,
        allowedRolesRequester=["relations_internationales"],
    )
    result = db_request(current_user, sql_request)

    validated_mobility = 0
    remaining_students = 0

    wishes_submitted = 0
    wishes_in_progress = 0
    retardataires = 0

    wishes_distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}

    if result:
        for row in result:
            if row.get("mobility_completed") == 1:
                validated_mobility += 1
            else:
                remaining_students += 1

            wish_count = row.get("wish_count", 0)
            last_sub = row.get("last_submission_date")

            # Distribution of wishes (for all students)
            if wish_count == 0:
                retardataires += 1
            else:
                last_sub_str = str(last_sub).strip().lower() if last_sub is not None else ""
                if last_sub_str and last_sub_str not in [
                    "none",
                    "null",
                    "0000-00-00 00:00:00",
                    "0000-00-00",
                    "0",
                ]:
                    wishes_submitted += 1
                else:
                    wishes_in_progress += 1

                # Update distribution (clamp to max 5)
                w_key = str(min(wish_count, 5))
                wishes_distribution[w_key] = wishes_distribution.get(w_key, 0) + 1

    return {
        "validated_mobility": validated_mobility,
        "remaining_students": remaining_students,
        "wishes_submitted": wishes_submitted,
        "wishes_in_progress": wishes_in_progress,
        "retardataires": retardataires,
        "wishes_distribution": wishes_distribution,
    }


@router.post(
    "/university/admin/mobility/assignment/close",
    tags=["admin", "mobility"],
    summary="Decline all pending assignments to close the acceptance phase",
    response_model=None,
)
def close_assignment_phase(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    with get_connection() as conn:
        sql_request = SQLRequest(
            request="UPDATE MOB_assignment SET status = 'declined' WHERE status = 'pending'",
            params=None,
            allowedRolesRequester=["relations_internationales"],
        )
        db_request(current_user, sql_request, conn=conn)
        sync_db_remaining_places(current_user, conn=conn)
    return {"message": "Toutes les affectations en attente ont été refusées."}


@router.post(
    "/university/admin/campaign/launch",
    tags=["admin", "mobility"],
    summary="Lancer la campagne et calculer les Z-scores",
    response_model=None,
)
def launch_mobility_campaign(
    payload: CampaignLaunchRequestPayload,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    with get_connection() as conn:
        # 1. Update doublants
        doublant_ids = []
        if payload.doublants:
            for d in payload.doublants:
                doublant_ids.append(d.id_etudiant)
                # Supprimer affectations / voeux existants pour le doublant
                db_request(
                    current_user,
                    SQLRequest(
                        request="DELETE FROM MOB_assignment WHERE id_etudiant = %(id)s",
                        params={"id": d.id_etudiant},
                        allowedRolesRequester=["relations_internationales"],
                    ),
                    conn=conn,
                )
                db_request(
                    current_user,
                    SQLRequest(
                        request="DELETE FROM MOB_wishes WHERE id_etudiant = %(id)s",
                        params={"id": d.id_etudiant},
                        allowedRolesRequester=["relations_internationales"],
                    ),
                    conn=conn,
                )
                # Maj du score
                db_request(
                    current_user,
                    SQLRequest(
                        request=(
                            "UPDATE LNM_etudiant SET mobility_z_score = %(z)s WHERE "
                            "id_etudiant = %(id)s"
                        ),
                        params={"z": d.z_score, "id": d.id_etudiant},
                        allowedRolesRequester=["relations_internationales"],
                    ),
                    conn=conn,
                )

        # 2. Calculer stats par filière pour les autres
        # On prend tous les étudiants de 4ème année ayant une note
        doublant_filter = ""
        if doublant_ids:
            doublant_filter = f"AND e.id_etudiant NOT IN ({','.join(map(str, doublant_ids))})"

        stats_query = f"""
            SELECT p.id_filiere, AVG(e.mobility_note) as mean_note,
                STDDEV(e.mobility_note) as std_note
            FROM LNM_etudiant e
            JOIN LNM_promo p ON e.id_promo = p.id_promo
            WHERE p.annee = 4 AND e.mobility_note IS NOT NULL {doublant_filter}
            GROUP BY p.id_filiere
        """
        stats_req = db_request(
            current_user,
            SQLRequest(
                request=stats_query,
                params=None,
                allowedRolesRequester=["relations_internationales"],
            ),
            conn=conn,
        )

        stats_map = {}
        if stats_req and isinstance(stats_req, list):
            for row in stats_req:
                stats_map[row["id_filiere"]] = row

        # 3. Récupérer et mettre à jour les autres étudiants
        students_query = f"""
            SELECT e.id_etudiant, e.mobility_note, p.id_filiere
            FROM LNM_etudiant e
            JOIN LNM_promo p ON e.id_promo = p.id_promo
            WHERE p.annee = 4 {doublant_filter}
        """
        students_req = db_request(
            current_user,
            SQLRequest(
                request=students_query,
                params=None,
                allowedRolesRequester=["relations_internationales"],
            ),
            conn=conn,
        )

        if students_req and isinstance(students_req, list):
            for student in students_req:
                note = student.get("mobility_note")
                f_id = student.get("id_filiere")
                z_score = 0.0
                if note is not None and f_id in stats_map:
                    f_stats = stats_map[f_id]
                    std = float(f_stats.get("std_note") or 0.0)
                    mean = float(f_stats.get("mean_note") or 0.0)
                    if std > 0:
                        z_score = round((float(note) - mean) / std, 4)

                # Update
                db_request(
                    current_user,
                    SQLRequest(
                        request=(
                            "UPDATE LNM_etudiant SET mobility_z_score = %(z)s WHERE "
                            "id_etudiant = %(id)s"
                        ),
                        params={"z": z_score, "id": student["id_etudiant"]},
                        allowedRolesRequester=["relations_internationales"],
                    ),
                    conn=conn,
                )

    return {"message": "Campagne lancée et scores calculés avec succès."}


@router.get(
    "/university/admin/campaign/doublant/{id_etudiant:int}",
    tags=["admin", "mobility"],
    summary="Vérifier un étudiant doublant avant l'ajout",
    response_model=None,
)
def verify_doublant(
    id_etudiant: int, current_user: Annotated[User, Depends(get_current_active_user)]
) -> object:
    query = """
        SELECT e.id_etudiant, e.nom, e.prenom, f.nom_filiere, p.annee
        FROM LNM_etudiant e
        JOIN LNM_promo p ON e.id_promo = p.id_promo
        JOIN LNM_filiere f ON p.id_filiere = f.id_filiere
        WHERE e.id_etudiant = %(id)s
    """
    req = SQLRequest(
        request=query,
        params={"id": id_etudiant},
        allowedRolesRequester=["relations_internationales"],
    )
    result = db_request(current_user, req)

    if not result:
        raise HTTPException(status_code=404, detail="Étudiant introuvable.")

    student = result[0]
    # L'utilisateur a demandé "si il est du 4 eme anne". On vérifie l'année.
    if student["annee"] != 4:
        raise HTTPException(
            status_code=400,
            detail=f"L'étudiant est en année {student['annee']} (doit être en 4ème année).",
        )

    return student
