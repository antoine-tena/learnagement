from pydantic import BaseModel, Field


class UniversityPlacePayload(BaseModel):
    id_filiere: int
    annee: int
    number_of_places: int = Field(ge=0)


class UniversityAdminPayload(BaseModel):
    name: str
    country: str
    code: str | None = None
    address: str | None = None
    latitude: float = 0.0
    longitude: float = 0.0
    website: str | None = None
    languages: str | None = None
    note_min: float | None = None
    type: str | None = "ERASMUS"
    S8_total_places: int = 0
    S9_total_places: int = 0
    places: list[UniversityPlacePayload] = []


class DoublantScore(BaseModel):
    id_etudiant: int
    z_score: float


class CampaignLaunchRequestPayload(BaseModel):
    doublants: list[DoublantScore] = []


class UpdateAssignmentStatusPayload(BaseModel):
    id_assignment: int
    new_status: str


class StudentDecisionPayload(BaseModel):
    decision: str
