"""Schémas Pydantic pour l'affectation de mobilité internationale."""

from pydantic import BaseModel


class MobilityQuota(BaseModel):
    id_filiere: int
    id_semestre: int
    places: int


class AssignmentRunPayload(BaseModel):
    annee_eligible: int = 4
    annee_scolaire: str = "2025-2026"
    mobility_quotas: list[MobilityQuota] = []


class MobilityQuotasUpdatePayload(BaseModel):
    annee_scolaire: str
    quotas: list[MobilityQuota]
