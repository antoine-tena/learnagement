"""Ce que le jeu fictif reprend du jeu public `db/freeData/Polytech_Annecy_Chambery/`.

Les promos, rôles et universités partenaires y sont désignés par leur nom, jamais par leur
numéro : le jeu fictif reste juste si le jeu public est renuméroté.
"""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from launcher.fake_data.sql import Raw

PUBLIC_SET_DIR = Path("db/freeData/Polytech_Annecy_Chambery")
PUBLIC_PARTNER_UNIVERSITIES = 91
COHORT_GROUP_TYPE = 1
LECTURE_SESSION_TYPE = 1


@dataclass(frozen=True)
class PublicCohort:
    """Une promo du jeu public : sa filière et son année d'études."""

    program: str
    year: int


PUBLIC_COHORTS = tuple(
    PublicCohort(program, year)
    for program in ("IDU", "MM", "SEA", "BAT", "EIT")
    for year in (3, 4, 5)
)


class PublicRole(StrEnum):
    """Les rôles du jeu public que tiennent les comptes de test."""

    STUDIES = "Responsable études"
    COMPANY_RELATIONS = "Relation entreprises"
    INTERNATIONAL = "Relations internationales"
    REGISTRAR = "Responsable de la scolarité"


def cohort_id(cohort: PublicCohort) -> Raw:
    """La sous-requête qui retrouve le numéro d'une promo du jeu public."""
    return Raw(
        "(SELECT `id_promo` FROM `LNM_promo` JOIN `LNM_filiere` USING (`id_filiere`) "
        f"WHERE `nom_filiere` = '{cohort.program}' AND `annee` = {cohort.year})"
    )


def role_id(role: PublicRole) -> Raw:
    """La sous-requête qui retrouve le numéro d'un rôle du jeu public."""
    return Raw(f"(SELECT `id_role` FROM `LNM_role` WHERE `role` = '{role.value}')")


def partner_university_id(rank: int) -> Raw:
    """La sous-requête de la `rank`-ième université partenaire du jeu public."""
    return Raw(
        "(SELECT `id_partner_university` FROM `MOB_partner_university` "
        f"ORDER BY `id_partner_university` LIMIT 1 OFFSET {rank})"
    )
