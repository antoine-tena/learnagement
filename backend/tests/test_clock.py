from datetime import UTC, datetime

from core.clock import CAMPUS_TIME_ZONE, campus_now, export_filename


def test_export_filename_uses_campus_time_from_a_utc_instant() -> None:
    winter_instant = datetime(2026, 1, 15, 23, 30, tzinfo=UTC)
    assert export_filename("Voeux", winter_instant) == "Export_Voeux_2026-01-16_00-30-00.xlsx"


def test_export_filename_follows_summer_time() -> None:
    summer_instant = datetime(2026, 7, 1, 10, 0, tzinfo=UTC)
    assert export_filename("Places", summer_instant) == "Export_Places_2026-07-01_12-00-00.xlsx"


def test_campus_now_is_aware() -> None:
    assert campus_now().tzinfo == CAMPUS_TIME_ZONE
