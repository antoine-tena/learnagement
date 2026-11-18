"""Les séances fictives, et donc leurs absences, tombent du lundi au vendredi."""

from datetime import timedelta

from launcher.fake_data import FakeDataSize, generate
from launcher.fake_data.activities import (
    SCHOOL_YEAR_START,
    session_day_offset,
    session_day_offset_sql,
)

LAST_WEEKDAY = 4
SESSION_IDS = range(1, 2000)


def test_school_year_starts_on_a_monday() -> None:
    assert SCHOOL_YEAR_START.weekday() == 0


def test_every_session_falls_on_a_weekday() -> None:
    for session_id in SESSION_IDS:
        day = SCHOOL_YEAR_START + timedelta(days=session_day_offset(session_id))
        assert day.weekday() <= LAST_WEEKDAY, (session_id, day)


def test_sql_offset_is_the_tested_one() -> None:
    sql = generate(FakeDataSize.SMALL)
    assert f"+ INTERVAL {session_day_offset_sql('`id_session`')} DAY" in sql
