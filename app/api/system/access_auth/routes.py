"""Routes FastAPI d'inspection des droits d'accès."""

import inspect
import re
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends

from api.dependencies import get_current_active_user
from models.user import User
from system.tools import get_all_local_requests, get_all_requests

from .sqlglot_lineage import build_lineage_tree
from .tree import build_tree

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get(
    "/access_auth",
    tags=["check", "table"],
    summary="Teacher without session",
    description="Check teacher without session.",
    response_model=None,
)
def get_access_auth(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    if "administratif" in current_user.roles:
        all_requests = get_all_requests(package_name="user") | get_all_local_requests()

        result = []
        for fichier, module_requests in all_requests.items():
            for endpoint_name, req in module_requests.items():
                # Extraire les champs SELECT de la requête SQL
                sql = req.get("request", "")
                select_match = re.search(r"SELECT\s+(.*?)\s+FROM", sql, re.IGNORECASE | re.DOTALL)
                if select_match:
                    fields = [
                        f.strip().split(" AS ")[0].strip() for f in select_match.group(1).split(",")
                    ]
                else:
                    fields = []

                # Un tuple par rôle autorisé
                allowed = req.get("allowedRolesRequester", [])
                if callable(allowed):
                    # C'est un lambda : on récupère son code source
                    source = inspect.getsource(allowed).strip()
                    roles = ["".join(source.split(":")[1:]).strip()]
                else:
                    roles = allowed

                for role in roles:
                    result.append(
                        {
                            "fichier": fichier,
                            "data_access": endpoint_name,
                            "data": ", ".join(fields),
                            "allowed_access": role,
                        }
                    )
        return result
    else:
        return {"response": "User not allowed"}


@router.get(
    "/access_auth_tree",
    tags=["check", "tree"],
    summary="Teacher without session",
    description="Check teacher without session.",
    response_model=None,
)
def get_access_auth_tree(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    response = {
        "success": None,
        "meta": {
            "version": "1",
            "type": "tree",
        },
        "data": None,
        "errors": None,
    }

    if "administratif" in current_user.roles:
        all_requests = get_all_requests(package_name="user") | get_all_local_requests()

        response["success"] = True
        response["data"] = build_tree(all_requests)
    else:
        response["success"] = False
        response["errors"] = [
            {
                "code": "ACCESS_DENIED",
                "message": "You are not authorized to access this resource.",
            }
        ]

    return response


@router.get(
    "/access_auth_tree_sqlglot",
    tags=["check", "tree"],
    summary="Teacher without session",
    description="Check teacher without session.",
    response_model=None,
)
def get_access_auth_tree_sqlglot(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> object:
    response = {
        "success": None,
        "meta": {
            "version": "1",
            "type": "tree",
        },
        "data": None,
        "errors": None,
    }

    if "administratif" in current_user.roles:
        all_requests = get_all_requests(package_name="user") | get_all_local_requests()

        response["success"] = True
        response["data"] = build_lineage_tree(all_requests)
    else:
        response["success"] = False
        response["errors"] = [
            {
                "code": "ACCESS_DENIED",
                "message": "You are not authorized to access this resource.",
            }
        ]

    return response
