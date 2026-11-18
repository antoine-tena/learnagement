"""Le numéro de semaine des pages de charge : celui de l'ISO, et un message sur une date fausse."""

from types import ModuleType

import pytest

from pages import charge_administratif, charge_enseignant

PAGES = (charge_administratif, charge_enseignant)


@pytest.mark.parametrize("page", PAGES)
@pytest.mark.parametrize(
    ("day", "week"),
    [("2026-11-18", 47), ("2027-01-01", 53), ("2027-01-04", 1)],
)
def test_week_number_is_the_iso_one(page: ModuleType, day: str, week: int) -> None:
    assert page.calculer_semaine(day) == week


@pytest.mark.parametrize("page", PAGES)
def test_wrong_date_gives_a_message(page: ModuleType) -> None:
    assert "Erreur" in page.calculer_semaine("18/11/2026")
