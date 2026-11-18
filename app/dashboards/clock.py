"""Heure et date du jour à Paris, le fuseau des enseignants et des administratifs."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")


def now_in_paris() -> datetime:
    """L'instant présent, avec le fuseau de Paris."""
    return datetime.now(PARIS)


def today_in_paris() -> date:
    """La date du jour à Paris, même quand le serveur tourne en UTC."""
    return now_in_paris().date()
