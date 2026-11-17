"""Algorithme Round-Robin d'affectation pour la mobilité internationale."""

import logging
from typing import Any

from .schemas import MobilityQuota

logger = logging.getLogger(__name__)


def run_round_robin_assignment(
    students: list[dict],
    wishes: list[dict],
    places: dict,
    mobility_quotas: list[MobilityQuota] | None = None,
) -> dict[str, Any]:
    """
    Étape 5: Logique d'affectation Round-Robin.

    Parcourt la liste des étudiants triés par Z-score décroissant.
    Pour chaque étudiant, examine ses vœux par ordre de priorité (1 à 5) :
      - Condition 1 : places globales S8 ou S9 restantes > 0 (toujours vrai si stage)
      - Condition 2 : places spécialité restantes > 0 (toujours vrai si stage)
      - Condition 3 : quota de départ restant (filière, semestre) > 0 (toujours vrai si stage)

    Si les 3 conditions sont satisfaites → affectation validée.
    Si aucun vœu n'est accepté → l'étudiant n'est pas inséré dans MOB_assignment.

    Retourne un dict :
      {
        "assignments"      : List[dict],  affectations validées
        "final_places"     : dict,        état des places restantes en mémoire
        "remaining_quotas" : dict          état des quotas restants par (filière, semestre)
      }
    Les quotas restants sont retournés en mémoire uniquement (pas persistés en base).
    """
    # --- Initialisation des places restantes (copie des capacités de référence) ---
    # global_places_left[str(id_university)]["S8"|"S9"] = places restantes
    global_places_left: dict[str, dict[str, int]] = {}
    for id_univ, semesters in (places.get("global_places") or {}).items():
        global_places_left[id_univ] = dict(semesters)  # copie

    # specialty_places_left[str(id_university)][f"{id_filiere}_{annee}"] = places restantes
    specialty_places_left: dict[str, dict[str, int]] = {}
    for id_univ, filieres in (places.get("specialty_places") or {}).items():
        specialty_places_left[id_univ] = dict(filieres)  # copie

    stages_set = set(places.get("stages") or [])

    # --- Initialisation des quotas restants (fournis par l'utilisateur) ---
    # remaining_quotas[id_filiere][id_semestre] = quota restant
    remaining_quotas: dict[int, dict[int, int]] = {}
    for q in mobility_quotas or []:
        if q.id_filiere not in remaining_quotas:
            remaining_quotas[q.id_filiere] = {}
        remaining_quotas[q.id_filiere][q.id_semestre] = q.places

    # --- Index des vœux par étudiant ---
    wishes_by_student: dict[int, list[dict]] = {}
    for w in wishes:
        student_id = w["id_etudiant"]
        if student_id not in wishes_by_student:
            wishes_by_student[student_id] = []
        wishes_by_student[student_id].append(w)
    # Les vœux sont déjà triés par priorité ASC depuis get_student_wishes

    # --- Boucle principale : parcours des étudiants par Z-score décroissant ---
    assignments = []
    for student in students:
        id_etudiant = student["id_etudiant"]
        id_filiere = student["id_filiere"]
        student_wishes = wishes_by_student.get(id_etudiant, [])

        assigned = False
        for wish in student_wishes:
            id_university = wish["id_partner_university"]
            id_univ_str = str(id_university)
            id_semestre = wish["id_semestre"]
            sem_key = "S8" if id_semestre == 8 else "S9"

            # Le frontend gère les places avec annee = 4 pour le S8, et annee = 5 pour le S9
            annee_for_wish = 4 if id_semestre == 8 else 5
            filiere_key = f"{id_filiere}_{annee_for_wish}"

            is_stage = id_university in stages_set

            # --- Condition 1 : places globales disponibles ---
            if is_stage:
                cond1 = True
            else:
                univ_global = global_places_left.get(id_univ_str, {})
                cond1 = univ_global.get(sem_key, 0) > 0

            if not cond1:
                logger.debug(
                    "Étudiant %s — vœu université %s sem %s refusé : places globales épuisées",
                    id_etudiant,
                    id_university,
                    id_semestre,
                )
                continue

            # --- Condition 2 : places spécialité disponibles ---
            if is_stage:
                cond2 = True
            else:
                univ_specialty = specialty_places_left.get(id_univ_str, {})
                cond2 = univ_specialty.get(filiere_key, 0) > 0

            if not cond2:
                logger.debug(
                    "Étudiant %s — vœu université %s sem %s refusé : places spécialité épuisées",
                    id_etudiant,
                    id_university,
                    id_semestre,
                )
                continue

            # --- Condition 3 : quota de départ restant ---
            if is_stage:
                cond3 = True
            else:
                quota_sem = remaining_quotas.get(id_filiere, {}).get(id_semestre, 0)
                cond3 = quota_sem > 0

            if not cond3:
                logger.debug(
                    "Étudiant %s — vœu université %s sem %s refusé : quota filière épuisé",
                    id_etudiant,
                    id_university,
                    id_semestre,
                )
                continue

            # --- Les 3 conditions sont satisfaites : affectation validée ---
            assignments.append(
                {
                    "id_etudiant": id_etudiant,
                    "id_partner_university": id_university,
                    "id_semestre": id_semestre,
                    "status": "pending",
                }
            )

            # Décrémentation des stocks (sauf stage)
            if not is_stage:
                global_places_left[id_univ_str][sem_key] -= 1
                specialty_places_left[id_univ_str][filiere_key] -= 1
                remaining_quotas[id_filiere][id_semestre] -= 1

            assigned = True
            break  # passer à l'étudiant suivant

        if not assigned:
            logger.debug(
                "Étudiant %s — aucun vœu accepté, non inséré dans MOB_assignment.", id_etudiant
            )
            # SUPPRESSION À LA DEMANDE DE L'UTILISATEUR :
            # Il n'y a plus d'affectation par défaut au stage pour les étudiants non affectés
            # (ni pour les retardataires, ni pour ceux dont les vœux ont tous été refusés).

    # --- Construction de l'état final des places restantes (pour persistance) ---
    final_places = {
        "global_places": global_places_left,
        "specialty_places": specialty_places_left,
    }

    return {
        "assignments": assignments,
        "final_places": final_places,
        "remaining_quotas": remaining_quotas,
    }
