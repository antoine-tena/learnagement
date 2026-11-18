from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.get(
    "/modules/{id_module}/dependencies",
    tags=["module"],
    summary="Get modules dependencies",
    description="Get all modules dependencies",
    response_model=None,
)
def get_module_dependencies(
    id_module: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT `id_sequence_prev`, `id_sequence_next`
            FROM `MAQUETTE_dependance_sequence`
                LEFT JOIN MAQUETTE_module_sequence on MAQUETTE_module_sequence.id_module_sequence
                    = MAQUETTE_dependance_sequence.id_sequence_prev
                LEFT JOIN MAQUETTE_module_sequencage
                    ON MAQUETTE_module_sequencage.id_module_sequencage
                        = MAQUETTE_module_sequence.id_module_sequencage
                LEFT JOIN MAQUETTE_module
                    ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                LEFT JOIN LNM_seance_type
                    ON LNM_seance_type.id_seance_type = MAQUETTE_module_sequencage.id_seance_type
            WHERE MAQUETTE_module.id_module = %(id_module_prev)s
            UNION
            SELECT `id_sequence_prev`, `id_sequence_next`
            FROM `MAQUETTE_dependance_sequence`
                LEFT JOIN MAQUETTE_module_sequence on MAQUETTE_module_sequence.id_module_sequence
                    = MAQUETTE_dependance_sequence.id_sequence_next
                LEFT JOIN MAQUETTE_module_sequencage
                    ON MAQUETTE_module_sequencage.id_module_sequencage
                        = MAQUETTE_module_sequence.id_module_sequencage
                LEFT JOIN MAQUETTE_module
                    ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                LEFT JOIN LNM_seance_type
                    ON LNM_seance_type.id_seance_type = MAQUETTE_module_sequencage.id_seance_type
            WHERE MAQUETTE_module.id_module = %(id_module_next)s
        """,
        "params": {
            "id_module_prev": id_module,
            "id_module_next": id_module,
        },
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/modules/{id_module}/sequence_dependencies",
    tags=["module"],
    summary="Get sequence dependencies",
    description="Get all modules sequence dependencies",
    response_model=None,
)
def get_module_sequence_dependencies(
    id_module: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT MAQUETTE_module_sequence.id_module_sequence,
                MAQUETTE_module_sequence.numero_ordre, LNM_seance_type.type,
                MAQUETTE_module.code_module, MAQUETTE_module.nom,
                MAQUETTE_module_sequence.commentaire
                    FROM MAQUETTE_module_sequence
                JOIN MAQUETTE_module_sequencage
                    ON MAQUETTE_module_sequencage.id_module_sequencage
                        = MAQUETTE_module_sequence.id_module_sequencage
                JOIN MAQUETTE_module
                    ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                JOIN LNM_seance_type
                    ON LNM_seance_type.id_seance_type = MAQUETTE_module_sequencage.id_seance_type
            WHERE MAQUETTE_module_sequence.id_module_sequence IN (
                    SELECT MAQUETTE_module_sequence.id_module_sequence
                    FROM MAQUETTE_module_sequence
                        JOIN MAQUETTE_module_sequencage
                            ON MAQUETTE_module_sequencage.id_module_sequencage
                                = MAQUETTE_module_sequence.id_module_sequencage
                        JOIN MAQUETTE_module
                            ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                    WHERE MAQUETTE_module.id_module = %(id_module)s)
            OR MAQUETTE_module_sequence.id_module_sequence IN (
                    SELECT `id_sequence_next`
                    FROM `MAQUETTE_dependance_sequence`
                        JOIN MAQUETTE_module_sequence as sequence_prev
                            on sequence_prev.id_module_sequence
                            = MAQUETTE_dependance_sequence.id_sequence_prev
                        JOIN MAQUETTE_module_sequencage  as sequencage_prev
                            ON sequencage_prev.id_module_sequencage
                                = sequence_prev.id_module_sequencage
                        JOIN MAQUETTE_module as module_prev
                            ON module_prev.id_module = sequencage_prev.id_module
                    WHERE module_prev.id_module = %(id_module_prev)s)
            OR MAQUETTE_module_sequence.id_module_sequence IN (
                    SELECT `id_sequence_prev`
                    FROM `MAQUETTE_dependance_sequence`
                        JOIN MAQUETTE_module_sequence as sequence_next
                            on sequence_next.id_module_sequence
                            = MAQUETTE_dependance_sequence.id_sequence_next
                        JOIN MAQUETTE_module_sequencage  as sequencage_next
                            ON sequencage_next.id_module_sequencage
                                = sequence_next.id_module_sequencage
                        JOIN MAQUETTE_module as module_next
                            ON module_next.id_module = sequencage_next.id_module
                    WHERE module_next.id_module = %(id_module_next)s)
        """,
        "params": {
            "id_module": id_module,
            "id_module_prev": id_module,
            "id_module_next": id_module,
        },
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/modules/gantt/{id_responsable}",
    tags=["module"],
    summary="Get sequence dependencies for Gantt",
    description="Get all modules sequence dependencies formatted for a Gantt chart",
    response_model=None,
)
def get_data_gantt_endpoint(
    id_responsable: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT
                        pmms.id_module_sequence AS "prv_id",
                        pmm.code_module AS "prv_code_module",
                pmm.nom AS "prv_nom",
                pmd.nom AS "prv_discipline",
                pls.semestre AS "prv_semestre",
                pmmsg.duree_h AS "prv_duree_h",
                CONCAT(plst.type, pmms.numero_ordre) AS "prv_type",
                nmms.id_module_sequence AS "nxt_id",
                nmm.code_module AS "nxt_code_module",
                nmd.nom AS "prv_discipline",
                nls.semestre AS "nxt_semestre",
                nmm.nom AS "nxt_nom",
                nmmsg.duree_h AS "nxt_duree_h",
                CONCAT(nlst.type, nmms.numero_ordre) AS "nxt_type"
            FROM MAQUETTE_dependance_sequence mds
                # PREVIOUS
                LEFT JOIN MAQUETTE_module_sequence pmms on pmms.id_module_sequence
                    = mds.id_sequence_prev
                JOIN MAQUETTE_module_sequencage pmmsg on pmmsg.id_module_sequencage
                    = pmms.id_module_sequencage
                JOIN LNM_seance_type plst on plst.id_seance_type = pmmsg.id_seance_type
                JOIN MAQUETTE_module pmm on pmm.id_module = pmmsg.id_module
                JOIN MAQUETTE_discipline pmd on pmd.id_discipline = pmm.id_discipline
                JOIN LNM_semestre pls on pls.id_semestre = pmm.id_semestre
                # NEXT
                LEFT JOIN MAQUETTE_module_sequence nmms on nmms.id_module_sequence
                    = mds.id_sequence_next
                JOIN MAQUETTE_module_sequencage nmmsg on nmmsg.id_module_sequencage
                    = nmms.id_module_sequencage
                JOIN LNM_seance_type nlst on nlst.id_seance_type = nmmsg.id_seance_type
                JOIN MAQUETTE_module nmm on nmm.id_module = nmmsg.id_module
                JOIN MAQUETTE_discipline nmd on nmd.id_discipline = nmm.id_discipline
                JOIN LNM_semestre nls on nls.id_semestre = nmm.id_semestre
                # FILTER BY RESPONSABLE
            WHERE pmm.id_responsable = %(id_responsable_prv)s or nmm.id_responsable
                = %(id_responsable_nxt)s;
        """,
        "params": {
            "id_responsable_prv": id_responsable,
            "id_responsable_nxt": id_responsable,
        },
        "allowedRolesRequester": {
            "roles": ["enseignant", "administratif"],
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/modules/gantt/etudiant/{id_etudiant}",
    tags=["module"],
    summary="Get sequence dependencies for Gantt",
    description="Get all modules sequence dependencies formatted for a Gantt chart for an etudiant",
    response_model=None,
)
def get_data_gantt_endpoint_etudiant(
    id_etudiant: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT
                pmms.id_module_sequence AS "prv_id",
                pmm.code_module        AS "prv_code_module",
                pmm.nom                AS "prv_nom",
                pmd.nom                AS "prv_discipline",
                pls.semestre           AS "prv_semestre",
                pmmsg.duree_h          AS "prv_duree_h",
                CONCAT(plst.type, pmms.numero_ordre) AS "prv_type",
                nmms.id_module_sequence AS "nxt_id",
                nmm.code_module        AS "nxt_code_module",
                nmm.nom                AS "nxt_nom",
                nmd.nom                AS "nxt_discipline",
                nls.semestre           AS "nxt_semestre",
                nmmsg.duree_h          AS "nxt_duree_h",
                CONCAT(nlst.type, nmms.numero_ordre) AS "nxt_type"

            FROM LNM_etudiant lnm_e

            -- Résolution de la promo de l'étudiant
            JOIN MAQUETTE_learning_unit etu_lu ON etu_lu.id_promo = lnm_e.id_promo

            JOIN MAQUETTE_module_as_learning_unit etu_malu
                ON etu_malu.id_learning_unit = etu_lu.id_learning_unit

            -- Point d'entrée dans les séquences via la promo
            JOIN MAQUETTE_module_sequence etu_mms
                ON etu_mms.id_module_sequencage IN (SELECT id_module_sequencage
                    FROM MAQUETTE_module_sequencage
                    WHERE id_module = etu_malu.id_module)

            JOIN MAQUETTE_dependance_sequence mds
                ON mds.id_sequence_prev = etu_mms.id_module_sequence
                OR mds.id_sequence_next = etu_mms.id_module_sequence

            -- === PREVIOUS ===
            LEFT JOIN MAQUETTE_module_sequence pmms
                ON pmms.id_module_sequence = mds.id_sequence_prev
            LEFT JOIN MAQUETTE_module_sequencage pmmsg
                ON pmmsg.id_module_sequencage = pmms.id_module_sequencage
            LEFT JOIN LNM_seance_type plst ON plst.id_seance_type = pmmsg.id_seance_type
            LEFT JOIN MAQUETTE_module pmm ON pmm.id_module = pmmsg.id_module
            LEFT JOIN MAQUETTE_module_as_learning_unit pmmalu ON pmmalu.id_module = pmm.id_module
            LEFT JOIN MAQUETTE_learning_unit pmlu ON pmlu.id_learning_unit = pmmalu.id_learning_unit
            LEFT JOIN MAQUETTE_discipline pmd ON pmd.id_discipline = pmm.id_discipline
            LEFT JOIN LNM_semestre pls ON pls.id_semestre = pmm.id_semestre

            -- === NEXT ===
            LEFT JOIN MAQUETTE_module_sequence nmms
                ON nmms.id_module_sequence = mds.id_sequence_next
            LEFT JOIN MAQUETTE_module_sequencage nmmsg
                ON nmmsg.id_module_sequencage = nmms.id_module_sequencage
            LEFT JOIN LNM_seance_type nlst ON nlst.id_seance_type = nmmsg.id_seance_type
            LEFT JOIN MAQUETTE_module nmm ON nmm.id_module = nmmsg.id_module
            LEFT JOIN MAQUETTE_module_as_learning_unit nmmalu ON nmmalu.id_module = nmm.id_module
            LEFT JOIN MAQUETTE_learning_unit nmlu ON nmlu.id_learning_unit = nmmalu.id_learning_unit
            LEFT JOIN MAQUETTE_discipline nmd ON nmd.id_discipline = nmm.id_discipline
            LEFT JOIN LNM_semestre nls ON nls.id_semestre = nmm.id_semestre

        WHERE lnm_e.id_etudiant = %(id_etudiant)s AND (pmlu.id_promo = lnm_e.id_promo
            OR nmlu.id_promo = lnm_e.id_promo)
        GROUP BY pmms.id_module_sequence, nmms.id_module_sequence;
        """,
        "params": {
            "id_etudiant": id_etudiant,
        },
        "allowedRolesRequester": ["connected_user"],
    }
    return db_request(current_user, SQLRequest(**request))
