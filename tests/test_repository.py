"""
Unit Tests for DayBalance Repository Data Access Layer
Validates CRUD operations, foreign key cascades, unique constraints, and profile isolation.
"""

from pathlib import Path
import pytest
from database.repository import (
    archive_habit, create_experiment, create_focus_session,
    create_goal, create_habit, create_profile, create_routine,
    delete_habit, delete_profile, delete_routine, get_daily_habit_entries_map,
    get_experiments, get_focus_sessions, get_goals, get_habit_by_id,
    get_habit_entries, get_habits, get_lifestyle_log, get_profile_by_id,
    get_profile_stats_for_deletion, get_profiles, get_routines, log_habit_entry,
    log_lifestyle, update_habit, update_profile, update_routine
)


def test_profile_lifecycle(test_db_path: Path):
    """Verifies profile creation, retrieval, updates, and isolation."""
    p_id = create_profile("Jane Doe", "jane@example.com", theme_preference="light", db_path=test_db_path)
    assert p_id > 0

    p = get_profile_by_id(p_id, db_path=test_db_path)
    assert p is not None
    assert p["name"] == "Jane Doe"
    assert p["theme_preference"] == "light"

    # Update profile
    success = update_profile(p_id, name="Jane Smith", theme_preference="dark", db_path=test_db_path)
    assert success is True

    updated = get_profile_by_id(p_id, db_path=test_db_path)
    assert updated["name"] == "Jane Smith"
    assert updated["theme_preference"] == "dark"


def test_profile_isolation(test_db_path: Path):
    """Ensures queries for Profile A never expose or leak data belonging to Profile B."""
    p1 = create_profile("User One", db_path=test_db_path)
    p2 = create_profile("User Two", db_path=test_db_path)

    # Add habit to p1
    h1 = create_habit(p1, "User 1 Secret Habit", "Custom", db_path=test_db_path)
    log_habit_entry(p1, h1, "2026-10-27", status="completed", db_path=test_db_path)

    # Check p2
    p2_habits = get_habits(p2, db_path=test_db_path)
    assert len(p2_habits) == 0

    p2_entries = get_habit_entries(p2, db_path=test_db_path)
    assert len(p2_entries) == 0


def test_habit_crud_and_archival(test_db_path: Path, sample_profile_id: int):
    """Tests creating, updating, archiving, and retrieving habits."""
    p_id = sample_profile_id
    h_id = create_habit(
        profile_id=p_id,
        name="Morning Hydration",
        category="Health & Fitness",
        measurement_type="numeric_target",
        target_value=2500.0,
        unit="ml",
        frequency="daily",
        db_path=test_db_path
    )
    assert h_id > 0

    h = get_habit_by_id(h_id, p_id, db_path=test_db_path)
    assert h["name"] == "Morning Hydration"
    assert h["target_value"] == 2500.0

    # Archive
    archive_habit(h_id, p_id, db_path=test_db_path)
    active_habits = get_habits(p_id, include_archived=False, db_path=test_db_path)
    assert not any(x["id"] == h_id for x in active_habits)

    all_habits = get_habits(p_id, include_archived=True, db_path=test_db_path)
    assert any(x["id"] == h_id for x in all_habits)


def test_habit_entry_upsert_and_target_preservation(test_db_path: Path, sample_profile_id: int):
    """
    Verifies that logging habit entries handles UPSERT (ON CONFLICT) safely
    and preserves historical target_at_entry without mutation.
    """
    p_id = sample_profile_id
    h_id = create_habit(p_id, "Read Pages", "Productivity & Deep Work", target_value=20.0, unit="pages", db_path=test_db_path)

    # Log entry
    e_id = log_habit_entry(
        profile_id=p_id,
        habit_id=h_id,
        entry_date="2026-10-25",
        status="completed",
        value_recorded=25.0,
        target_at_entry=20.0,
        db_path=test_db_path
    )
    assert e_id > 0

    # Update habit's target to 30.0
    update_habit(h_id, p_id, target_value=30.0, db_path=test_db_path)

    # Check that previous entry still has target_at_entry = 20.0
    entries_map = get_daily_habit_entries_map(p_id, "2026-10-25", db_path=test_db_path)
    assert h_id in entries_map
    assert entries_map[h_id]["target_at_entry"] == 20.0
    assert entries_map[h_id]["value_recorded"] == 25.0

    # Re-logging on same date updates existing entry
    log_habit_entry(
        profile_id=p_id,
        habit_id=h_id,
        entry_date="2026-10-25",
        status="completed",
        value_recorded=35.0,
        target_at_entry=20.0,
        notes="Bonus reading evening",
        db_path=test_db_path
    )
    updated_map = get_daily_habit_entries_map(p_id, "2026-10-25", db_path=test_db_path)
    assert updated_map[h_id]["value_recorded"] == 35.0
    assert updated_map[h_id]["notes"] == "Bonus reading evening"


def test_profile_cascade_deletion(test_db_path: Path):
    """Confirms cascading delete erases all child records when a profile is removed."""
    p_id = create_profile("Disposable Profile", db_path=test_db_path)
    h_id = create_habit(p_id, "Test Habit", "Custom", db_path=test_db_path)
    log_habit_entry(p_id, h_id, "2026-10-20", db_path=test_db_path)
    log_lifestyle(p_id, "2026-10-20", sleep_hours=7.0, study_minutes=60, db_path=test_db_path)
    create_focus_session(p_id, "Quick Focus", 25, db_path=test_db_path)

    stats = get_profile_stats_for_deletion(p_id, db_path=test_db_path)
    assert stats["habits"] == 1
    assert stats["habit_entries"] == 1
    assert stats["daily_lifestyle_logs"] == 1
    assert stats["focus_sessions"] == 1

    delete_profile(p_id, db_path=test_db_path)
    after_stats = get_profile_stats_for_deletion(p_id, db_path=test_db_path)
    assert sum(after_stats.values()) == 0
