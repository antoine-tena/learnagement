from pydantic import BaseModel, ConfigDict, Field


class ModuleCreation(BaseModel):
    """Corps de `POST /modules` : les noms reçus sont ceux du formulaire de `web/`."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    code_module: str = Field(min_length=1, max_length=20)
    nom: str = Field(min_length=1, max_length=80)
    hours_cm: float = Field(default=0, ge=0, alias="hCM")
    hours_td: float = Field(default=0, ge=0, alias="hTD")
    hours_tp: float = Field(default=0, ge=0, alias="hTP")
    hours_project: float = Field(default=0, ge=0, alias="hProj")
    hours_personal: float = Field(default=0, ge=0, alias="hPerso")
    ects: float = Field(default=0, ge=0, alias="ECTS")
    id_semestre: int = Field(alias="semestre")
    id_responsable: int | None = None
    id_discipline: int
