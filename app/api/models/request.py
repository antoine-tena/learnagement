from collections.abc import Callable

from pydantic import BaseModel

AccessRule = (
    str  # "anonymous" | "connected_user"
    | list[str]  # ["administratif", "enseignant"]
    | dict  # {"roles": [...], "any": {...}, "all": [...], "hierarchy": [...]},
    | Callable  # lambda rule
)


class SQLRequest(BaseModel):
    request: str
    params: dict | None = None
    # Nom d'origine gardé : plus de 200 appels, dont ceux des étudiants.
    allowedRolesRequester: AccessRule  # noqa: N815

    model_config = {"arbitrary_types_allowed": True}
