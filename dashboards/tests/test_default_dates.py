"""Les dates par défaut des pages de charge et de stages suivent le jour de Paris."""

import sys
from datetime import UTC, date, datetime, tzinfo
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import clock

BEFORE_MIDNIGHT_UTC = datetime(2026, 11, 18, 22, 30, tzinfo=UTC)
AFTER_MIDNIGHT_UTC = datetime(2026, 11, 18, 23, 30, tzinfo=UTC)


def freeze(monkeypatch: pytest.MonkeyPatch, instant: datetime) -> None:
    """Fige l'horloge de `clock` sur `instant`."""

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> datetime:  # type: ignore[override]  # signature de datetime
            return instant.astimezone(tz)

    monkeypatch.setattr(clock, "datetime", FrozenDatetime)


def find_date_picker(component: object) -> object:
    """Le sélecteur de dates `dates_input` dans l'arbre du layout."""
    if getattr(component, "id", None) == "dates_input":
        return component
    children = getattr(component, "children", None)
    for child in children if isinstance(children, list) else [children]:
        if child is not None and not isinstance(child, str):
            found = find_date_picker(child)
            if found is not None:
                return found
    return None


def test_today_is_paris_day_after_midnight_utc_shift(monkeypatch: pytest.MonkeyPatch) -> None:
    freeze(monkeypatch, AFTER_MIDNIGHT_UTC)
    assert clock.today_in_paris() == date(2026, 11, 19)


def test_charge_semester_follows_paris_day(monkeypatch: pytest.MonkeyPatch) -> None:
    from pages import charge_administratif, charge_enseignant

    # 2027-01-14 23:30 UTC est déjà le 15 janvier à Paris : le semestre pair commence.
    freeze(monkeypatch, datetime(2027, 1, 14, 23, 30, tzinfo=UTC))
    assert charge_enseignant.get_semester() == 0
    assert charge_administratif.get_semester() == 0


def test_stages_default_dates_follow_paris_day(monkeypatch: pytest.MonkeyPatch) -> None:
    from pages.stages_administratif import app10_administratif_layout

    freeze(monkeypatch, BEFORE_MIDNIGHT_UTC)
    picker = find_date_picker(app10_administratif_layout())
    assert picker.start_date == date(2026, 11, 18)  # type: ignore[attr-defined]

    freeze(monkeypatch, AFTER_MIDNIGHT_UTC)
    picker = find_date_picker(app10_administratif_layout())
    assert picker.start_date == date(2026, 11, 19)  # type: ignore[attr-defined]
    assert picker.end_date == date(2026, 11, 19)  # type: ignore[attr-defined]
