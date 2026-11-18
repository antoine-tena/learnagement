"""L'heure du campus : les notions de calendrier (jour, mois, horodatage lu par un humain)."""

from datetime import datetime
from zoneinfo import ZoneInfo

CAMPUS_TIME_ZONE = ZoneInfo("Europe/Paris")
EXPORT_STAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"


def campus_now() -> datetime:
    """L'instant présent, à l'heure du campus."""
    return datetime.now(CAMPUS_TIME_ZONE)


def export_filename(label: str, moment: datetime | None = None) -> str:
    """Nom d'un export Excel, horodaté à l'heure du campus."""
    stamp = (moment or campus_now()).astimezone(CAMPUS_TIME_ZONE)
    return f"Export_{label}_{stamp.strftime(EXPORT_STAMP_FORMAT)}.xlsx"
