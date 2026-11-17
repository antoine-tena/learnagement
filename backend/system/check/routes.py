"""Routes FastAPI de vérification de cohérence des données."""

import inspect
import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import Rows, db_request, get_current_active_user
from models.request import SQLRequest
from models.user import User

from .requests_base import BASE_REQUESTS
from .requests_sequencage import SEQUENCAGE_REQUESTS

logger = logging.getLogger(__name__)

router = APIRouter()

requests = BASE_REQUESTS | SEQUENCAGE_REQUESTS


##################
# Enseignant
##################
@router.get(
    "/enseignant_sans_cours",
    tags=["check"],
    summary="Teacher without session",
    description="Check teacher without session.",
    response_model=None,
)
def check_lnm_enseignant_sans_cours(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = requests["get_" + inspect.currentframe().f_code.co_name]
    return db_request(current_user, SQLRequest(**request))


#########################
# Module
#########################
@router.get(
    "/module_sans_unite_d_enseignement",
    tags=["check"],
    summary="Module without learning unit",
    description="Check module not link to a learning unit.",
    response_model=None,
)
def check_maquette_module_without_learning_unit(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = requests["get_" + inspect.currentframe().f_code.co_name]
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/module_sans_apprentissage_critique",
    tags=["check"],
    summary="Module without apprentissage critique",
    description="Check module without apprentissage critique.",
    response_model=None,
)
def module_sans_apprentissage_critique(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = requests["get_" + inspect.currentframe().f_code.co_name]
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/module_detail_ects",
    tags=["check"],
    summary="ECTs weight",
    description="Check ratio hours ECTs.",
    response_model=None,
)
def module_detail_ects(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = requests["get_" + inspect.currentframe().f_code.co_name]
    return db_request(current_user, SQLRequest(**request))


########################
# Class
########################


@router.get(
    "/session_sans_intervenant",
    tags=["check"],
    summary="Session without teacher",
    description="Check session without teacher.",
    response_model=None,
)
def session_sans_intervenant(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = requests["get_" + inspect.currentframe().f_code.co_name]
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/session_reference_corruption",
    tags=["check"],
    summary="Session foreign K coruption",
    description="Check session not linked to module.",
    response_model=None,
)
def session_reference_corruption(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = requests["get_" + inspect.currentframe().f_code.co_name]
    return db_request(current_user, SQLRequest(**request))


# ToDo to finished
@router.get(
    "/maquette_vs_sequencage",
    tags=["check"],
    summary="Session hours Vs Program",
    description="Check whether the number of sequencage hours corresponds to the program.",
    response_model=None,
)
def maquette_vs_sequencage(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = requests["get_" + inspect.currentframe().f_code.co_name]
    return db_request(current_user, SQLRequest(**request))


@router.get(
    "/maquette_vs_sequencage/{id_responsable}",
    tags=["check"],
    summary="Session hours Vs Program",
    description="Check whether the number of sequencage hours corresponds to the program.",
    response_model=None,
)
def maquette_vs_sequencage_by_id_resp(
    id_responsable: int,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Rows:
    request = requests["get_" + inspect.currentframe().f_code.co_name]
    request["params"] = (
        request["params"](id_responsable) if callable(request["params"]) else request["params"]
    )
    request["allowedRolesRequester"] = (
        request["allowedRolesRequester"](id_responsable, current_user)
        if callable(request["allowedRolesRequester"])
        else request["allowedRolesRequester"]
    )
    return db_request(current_user, SQLRequest(**request))
