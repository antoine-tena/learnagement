"""Requêtes SQL et préparation des données pour l'affectation de mobilité."""

from models.request import SQLRequest
from models.user import User

from ._db import db_request, get_connection
from .schemas import MobilityQuota


def get_eligible_students(current_user: User) -> list[dict]:
    """
    Étape 1: Récupérer les étudiants éligibles (4ème année uniquement).
    Retourne une liste de dictionnaires avec id_etudiant, mobility_note, id_promo,
        id_filiere et submission_date.
    """
    query = """
        SELECT e.id_etudiant, e.mobility_z_score as z_score, e.id_promo, p.id_filiere, p.annee,
            MAX(w.submission_date) as submission_date
        FROM LNM_etudiant e
        JOIN LNM_promo p ON e.id_promo = p.id_promo
        JOIN MOB_wishes w ON e.id_etudiant = w.id_etudiant
        WHERE p.annee = 4
          AND w.submission_date IS NOT NULL
          AND e.mobility_z_score IS NOT NULL
        GROUP BY e.id_etudiant, e.mobility_z_score, e.id_promo, p.id_filiere, p.annee
    """
    request = {
        "request": query,
        "params": {},
        "allowedRolesRequester": ["relations_internationales"],
    }
    sql_request = SQLRequest(**request)
    result = db_request(current_user, sql_request)
    return result if result else []


def get_mobility_quotas_from_db(annee_scolaire: str, current_user: User) -> list[MobilityQuota]:
    """
    Récupère les quotas depuis la base de données pour une année scolaire donnée.
    """
    query = """
        SELECT id_filiere, id_semestre, places
        FROM MOB_filiere_quotas
        WHERE annee_scolaire = %(annee_scolaire)s
    """
    request = {
        "request": query,
        "params": {"annee_scolaire": annee_scolaire},
        "allowedRolesRequester": ["relations_internationales"],
    }
    sql_request = SQLRequest(**request)
    result = db_request(current_user, sql_request)

    quotas = []
    if result:
        for row in result:
            quotas.append(
                MobilityQuota(
                    id_filiere=row["id_filiere"],
                    id_semestre=row["id_semestre"],
                    places=row["places"],
                )
            )
    return quotas


def sort_students_by_z_score(students: list[dict]) -> list[dict]:
    """
    Étape 2: Trier les étudiants par Z-score (lu en BDD) décroissant
    (et date de soumission des vœux en cas d'égalité).
    """
    sorted_students = sorted(
        students, key=lambda x: (-float(x["z_score"] or 0), x["submission_date"])
    )
    return sorted_students


def get_student_wishes(current_user: User) -> list[dict]:
    """
    Étape 3: Récupérer tous les vœux soumis (submission_date IS NOT NULL).
    Trie par id_etudiant puis par priorité croissante.
    """
    query = """
        SELECT w.id_etudiant, w.id_partner_university, w.id_semestre, w.priority
        FROM MOB_wishes w
        JOIN LNM_etudiant e ON w.id_etudiant = e.id_etudiant
        JOIN LNM_promo p ON e.id_promo = p.id_promo
        WHERE w.submission_date IS NOT NULL
          AND p.annee = 4
        ORDER BY w.id_etudiant ASC, w.priority ASC
    """
    request = {
        "request": query,
        "params": {},
        "allowedRolesRequester": ["relations_internationales"],
    }
    sql_request = SQLRequest(**request)
    result = db_request(current_user, sql_request)
    return result if result else []


def get_available_places(current_user: User) -> dict:
    """
    Étape 4: Récupérer les places disponibles par université et promo.

    Récupère en priorité les capacités de référence nécessaires à l'exécution
    de l'algorithme :
      - number_of_places : capacité initiale par spécialité/promo (MOB_partner_university_places)
      - S8_total_places  : capacité globale S8 par université (MOB_partner_university)
      - S9_total_places  : capacité globale S9 par université (MOB_partner_university)

    Les colonnes de suivi des places restantes (S8_remaining_places,
    S9_remaining_places, remaining_places) sont des sorties de l'algorithme ;
    elles sont mises à jour via save_assignments après le calcul.

    Gère la spécificité des stages (places illimitées).
    """
    # 1. Capacités de référence par spécialité/filiere
    query_places = """
        SELECT id_partner_university, id_filiere, annee, number_of_places
        FROM MOB_partner_university_places
    """
    sql_places = SQLRequest(
        request=query_places, params={}, allowedRolesRequester=["relations_internationales"]
    )
    places_rows = db_request(current_user, sql_places) or []

    # 2. Capacités globales de référence par semestre (S8 / S9)
    query_global = """
        SELECT id_partner_university, S8_total_places, S9_total_places
        FROM MOB_partner_university
        WHERE type != 'stage'
          AND (S8_total_places IS NOT NULL OR S9_total_places IS NOT NULL)
    """
    sql_global = SQLRequest(
        request=query_global, params={}, allowedRolesRequester=["relations_internationales"]
    )
    global_rows = db_request(current_user, sql_global) or []

    # 3. Identifier les stages (places illimitées)
    query_stages = """
        SELECT id_partner_university
        FROM MOB_partner_university
        WHERE type = 'stage'
    """
    sql_stages = SQLRequest(
        request=query_stages, params={}, allowedRolesRequester=["relations_internationales"]
    )
    stage_rows = db_request(current_user, sql_stages) or []

    # Formatage : specialty_places[str(id_university)][f"{id_filiere}_{annee}"] = nombre_de_places
    specialty_places = {}
    for row in places_rows:
        id_univ = str(row["id_partner_university"])
        filiere_key = f"{row['id_filiere']}_{row['annee']}"
        if id_univ not in specialty_places:
            specialty_places[id_univ] = {}
        specialty_places[id_univ][filiere_key] = int(row["number_of_places"])

    # Formatage : global_places[str(id_university)] = {"S8": n, "S9": n}
    global_places = {}
    for row in global_rows:
        id_univ = str(row["id_partner_university"])
        global_places[id_univ] = {
            "S8": int(row["S8_total_places"]) if row["S8_total_places"] is not None else 0,
            "S9": int(row["S9_total_places"]) if row["S9_total_places"] is not None else 0,
        }

    stages_list = [row["id_partner_university"] for row in stage_rows]

    return {
        "specialty_places": specialty_places,  # capacités de référence par spécialité
        "global_places": global_places,  # capacités de référence globales S8/S9
        "stages": stages_list,
    }


def save_assignments(assignments: list[dict], final_places: dict, current_user: User) -> None:
    """
    Étape 6: Sauvegarder les affectations (statut 'pending') dans MOB_assignment
    et mettre à jour les places restantes en base de données.

    Met à jour :
      - S8_remaining_places / S9_remaining_places dans MOB_partner_university
      - remaining_places dans MOB_partner_university_places
    """
    with get_connection() as conn:
        # --- 6a. Supprimer les affectations précédentes non validées pour éviter les fantômes ---
        delete_pending = SQLRequest(
            request="DELETE FROM MOB_assignment WHERE status = 'pending'",
            params={},
            allowedRolesRequester=["relations_internationales"],
        )
        db_request(current_user, delete_pending, conn=conn)

        # --- 6b. Insérer les nouvelles affectations dans MOB_assignment ---
        if assignments:
            values_clause = []
            params = {}
            for i, assign in enumerate(assignments):
                status = assign.get("status", "pending")
                values_clause.append(f"(%(e{i})s, %(u{i})s, %(s{i})s, %(st{i})s)")
                params[f"e{i}"] = assign["id_etudiant"]
                params[f"u{i}"] = assign["id_partner_university"]
                params[f"s{i}"] = assign["id_semestre"]
                params[f"st{i}"] = status

            query = f"""
                INSERT INTO MOB_assignment (id_etudiant, id_partner_university, id_semestre, status)
                VALUES {", ".join(values_clause)}
                ON DUPLICATE KEY UPDATE
                    id_partner_university = VALUES(id_partner_university),
                    id_semestre           = VALUES(id_semestre),
                    status                = VALUES(status)
            """
            sql_request = SQLRequest(
                request=query, params=params, allowedRolesRequester=["relations_internationales"]
            )
            db_request(current_user, sql_request, conn=conn)
