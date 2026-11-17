from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import Rows, get_current_active_user
from models.request import SQLRequest
from models.user import User

from ._db import db_request

router = APIRouter()


@router.get(
    "/modules/sequencages/{id_responsable}",
    tags=["module"],
    summary="Get modules by responsible",
    description="Get all modules of a responsible",
    response_model=None,
)
def get_sequencages_responsable(
    id_responsable: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT  MAQUETTE_module_sequencage.`id_module_sequencage`,
                    MAQUETTE_module_sequencage.`id_module`,
                    MAQUETTE_module_sequencage.`nombre`,
                    CAST(MAQUETTE_module_sequencage.`duree_h` AS FLOAT) AS duree_h,
                    MAQUETTE_module.code_module,
                    LNM_seance_type.type,
                    LNM_groupe_type.groupe_type,
                    ExplicitSecondaryKs_LNM_enseignant.ExplicitSecondaryK as intervenant_principal
            FROM MAQUETTE_module_sequencage
                LEFT JOIN MAQUETTE_module
                    ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                LEFT JOIN LNM_seance_type
                    ON LNM_seance_type.id_seance_type = MAQUETTE_module_sequencage.id_seance_type
                LEFT JOIN LNM_groupe_type
                    ON LNM_groupe_type.id_groupe_type = MAQUETTE_module_sequencage.id_groupe_type
                LEFT JOIN ExplicitSecondaryKs_LNM_enseignant
                    ON ExplicitSecondaryKs_LNM_enseignant.id_enseignant
                        = MAQUETTE_module_sequencage.id_intervenant_principal
            WHERE MAQUETTE_module.id_responsable = %(id_responsable)s
        """,
        "params": {
            "id_responsable": id_responsable,
        },
        "allowedRolesRequester": {
            "roles": ["enseignant", "administratif"],
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/modules/sequences/{id_responsable}",
    tags=["module"],
    summary="Get modules by responsible",
    description="Get all modules of a responsible",
    response_model=None,
)
def get_sequences_responsable(
    id_responsable: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT  MAQUETTE_module_sequence.id_module_sequence AS id_sequence,
                    MAQUETTE_module_sequence.numero_ordre,
                    MAQUETTE_module_sequence.id_intervenant_principal,
                    MAQUETTE_module_sequence.commentaire,
                    MAQUETTE_module_sequencage.id_module,
                    MAQUETTE_module_sequencage.id_seance_type,
                    MAQUETTE_module_sequencage.id_groupe_type,
                    CAST(MAQUETTE_module_sequencage.duree_h AS FLOAT) AS duree_h,
                    MAQUETTE_module.code_module,
                    LNM_seance_type.type,
                    LNM_groupe_type.groupe_type,
                    ExplicitSecondaryKs_LNM_enseignant.ExplicitSecondaryK as intervenant_principal
            FROM MAQUETTE_module_sequence
                LEFT JOIN MAQUETTE_module_sequencage
                 ON MAQUETTE_module_sequencage.id_module_sequencage
                     = MAQUETTE_module_sequence.id_module_sequencage
                LEFT JOIN MAQUETTE_module
                    ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                LEFT JOIN LNM_seance_type
                    ON LNM_seance_type.id_seance_type = MAQUETTE_module_sequencage.id_seance_type
                LEFT JOIN LNM_groupe_type
                    ON LNM_groupe_type.id_groupe_type = MAQUETTE_module_sequencage.id_groupe_type
                LEFT JOIN ExplicitSecondaryKs_LNM_enseignant
                    ON ExplicitSecondaryKs_LNM_enseignant.id_enseignant
                        = MAQUETTE_module_sequence.id_intervenant_principal
            WHERE MAQUETTE_module.id_responsable = %(id_responsable)s
        """,
        "params": {
            "id_responsable": id_responsable,
        },
        "allowedRolesRequester": {
            "roles": ["enseignant", "administratif"],
        },
    }
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/modules/sessions/{id_responsable}",
    tags=["module"],
    summary="Get modules by responsible",
    description="Get all modules of a responsible",
    response_model=None,
)
def get_sessions_responsable(
    id_responsable: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = {
        "request": """
            SELECT
                        CLASS_session.id_session,
                CLASS_session.id_groupe,
                LNM_groupe.nom_groupe,
                LNM_promo.id_promo,
                ExplicitSecondaryKs_LNM_promo.ExplicitSecondaryK as promo,
                MAQUETTE_module_sequence.numero_ordre,
                MAQUETTE_module_sequence.id_intervenant_principal,
                MAQUETTE_module_sequence.commentaire,
                MAQUETTE_module_sequencage.id_module,
                MAQUETTE_module_sequencage.id_seance_type,
                CAST(MAQUETTE_module_sequencage.duree_h AS FLOAT) AS duree_h,
                MAQUETTE_module.code_module,
                LNM_seance_type.type,
                ExplicitSecondaryKs_LNM_enseignant.ExplicitSecondaryK as intervenant
                    FROM CLASS_session
                LEFT JOIN LNM_groupe ON LNM_groupe.id_groupe = CLASS_session.id_groupe
                LEFT JOIN LNM_promo ON LNM_promo.id_promo = LNM_groupe.id_promo
                LEFT JOIN ExplicitSecondaryKs_LNM_promo
                    ON ExplicitSecondaryKs_LNM_promo.id_promo = LNM_promo.id_promo
                LEFT JOIN MAQUETTE_module_sequence
                 ON MAQUETTE_module_sequence.id_module_sequence = CLASS_session.id_module_sequence
                LEFT JOIN MAQUETTE_module_sequencage
                 ON MAQUETTE_module_sequencage.id_module_sequencage
                     = MAQUETTE_module_sequence.id_module_sequencage
                LEFT JOIN MAQUETTE_module
                    ON MAQUETTE_module.id_module = MAQUETTE_module_sequencage.id_module
                LEFT JOIN LNM_seance_type
                    ON LNM_seance_type.id_seance_type = MAQUETTE_module_sequencage.id_seance_type
                LEFT JOIN LNM_groupe_type
                    ON LNM_groupe_type.id_groupe_type = MAQUETTE_module_sequencage.id_groupe_type
                LEFT JOIN ExplicitSecondaryKs_LNM_enseignant
                    ON ExplicitSecondaryKs_LNM_enseignant.id_enseignant
                        = CLASS_session.id_enseignant
            WHERE MAQUETTE_module.id_responsable = %(id_responsable)s
        """,
        "params": {
            "id_responsable": id_responsable,
        },
        "allowedRolesRequester": {
            "roles": ["enseignant", "administratif"],
        },
    }
    return db_request(current_user, SQLRequest(**request))
