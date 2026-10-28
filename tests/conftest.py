"""
DayBalance Test Configuration & Fixtures
Provides isolated temporary SQLite databases for reliable, side-effect-free testing.
"""

from datetime import date, timedelta
from pathlib import Path
import pytest
from database.connection import get_db_connection
from database.migrations import init_db
from database.repository import (
    create_habit, create_profile, create_routine,
    log_habit_entry, log_lifestyle
)


@pytest.fixture
def test_db_path(tmp_path: Path) -> Path:
    """Creates a temporary isolated SQLite database file and initializes the schema."""
    db_file = tmp_path / "test_daybalance.db"
    init_db(db_file)
    return db_file


@pytest.fixture
def sample_profile_id(test_db_path: Path) -> int:
    """Creates a test user profile."""
    return create_profile(
        name="Test User",
        email="test.user@example.com",
        theme_preference="dark",
        db_path=test_db_path
    )


@pytest.fixture
def seeded_test_data(test_db_path: Path, sample_profile_id: int) -> dict:
    """
    Populates sample habits, routines, entries, and lifestyle logs across 14 test days.
    """
    p_id = sample_profile_id
    today = date.today()
    two_weeks_ago = (today - timedelta(days=14)).isoformat()

    # Routine
    r_id = create_routine(p_id, "Morning Focus", "morning", "Start day right", db_path=test_db_path)

    # Habit 1: Daily Study (Duration)
    h_study = create_habit(
        profile_id=p_id,
        name="Study Machine Learning",
        category="Study & Academic",
        measurement_type="duration_minutes",
        target_value=120.0,
        unit="mins",
        frequency="daily",
        start_date=two_weeks_ago,
        routine_id=r_id,
        db_path=test_db_path
    )

    # Habit 2: Weekday Exercise
    h_ex = create_habit(
        profile_id=p_id,
        name="Gym & Movement",
        category="Movement & Active",
        measurement_type="duration_minutes",
        target_value=30.0,
        unit="mins",
        frequency="weekdays",
        frequency_days=[0, 1, 2, 3, 4],
        start_date=two_weeks_ago,
        db_path=test_db_path
    )

    # Habit 3: Reading (Count)
    h_read = create_habit(
        profile_id=p_id,
        name="Read Tech Book",
        category="Productivity & Deep Work",
        measurement_type="count",
        target_value=20.0,
        unit="pages",
        frequency="daily",
        start_date=two_weeks_ago,
        db_path=test_db_path
    )

    # Populate 14 days of entries and lifestyle logs
    for i in range(14, -1, -1):
        cur_d = today - timedelta(days=i)
        d_str = cur_d.isoformat()
        is_wknd = cur_d.weekday() >= 5

        # Lifestyle log
        sleep = 8.0 if i % 2 == 0 else 6.5
        study = 130 if sleep >= 7.5 else 75
        log_lifestyle(
            profile_id=p_id,
            log_date=d_str,
            sleep_hours=sleep,
            sleep_quality=4 if sleep >= 7.5 else 2,
            study_minutes=study,
            focus_sessions_count=2,
            exercise_minutes=45 if not is_wknd else 0,
            exercise_type="Strength" if not is_wknd else None,
            mood_score=4 if sleep >= 7.5 else 3,
            energy_score=4 if not is_wknd else 3,
            reflection_notes=f"Test log for day {i}",
            db_path=test_db_path
        )

        # Habit entries
        # Study completed daily
        log_habit_entry(
            profile_id=p_id,
            habit_id=h_study,
            entry_date=d_str,
            status="completed",
            value_recorded=study,
            target_at_entry=120.0,
            db_path=test_db_path
        )

        # Exercise completed weekdays, rest on weekends
        if not is_wknd:
            log_habit_entry(
                profile_id=p_id,
                habit_id=h_ex,
                entry_date=d_str,
                status="completed",
                value_recorded=45.0,
                target_at_entry=30.0,
                db_path=test_db_path
            )

        # Reading completed most days
        log_habit_entry(
            profile_id=p_id,
            habit_id=h_read,
            entry_date=d_str,
            status="completed" if i != 5 else "skipped",
            value_recorded=25.0 if i != 5 else 0.0,
            target_at_entry=20.0,
            skip_reason="Busy" if i == 5 else None,
            db_path=test_db_path
        )

    return {
        "profile_id": p_id,
        "habits": [h_study, h_ex, h_read],
        "routine_id": r_id,
        "db_path": test_db_path
    }
