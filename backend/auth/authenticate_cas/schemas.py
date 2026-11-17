"""Schéma de provisionnement CAS."""

from pydantic import BaseModel


class CasUserProvision(BaseModel):
    login: str
    email: str
    nom: str
    prenom: str
    members: list[str] = []
