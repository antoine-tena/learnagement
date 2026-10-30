from pydantic import BaseModel

# Type récursif pour allowedRolesRequester
AccessRule = (
    str  # "anonymous" | "connected_user"
    | list[str]  # ["administratif", "enseignant"]
    | dict  # {"roles": [...], "one": {...}, "all": {...}, "hierarchy": {...}}
)


class Responsibility(BaseModel):
    type_objet: str
    dimensions: dict[str, str] = {}  # {"resp": "stage", "filiere": "IDU", "niveau": "FI4", ...}
