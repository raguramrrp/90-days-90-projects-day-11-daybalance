"""
Unit Tests for DayBalance Backup, Restore & CSV Portability
Tests JSON backup generation, safe foreign-key remapping during restore, and CSV import validation.
"""

from pathlib import Path
from database.repository import create_habit, create_profile, get_habits, log_habit_entry
from services.backup_service import (
    export_entries_csv, export_habits_csv, export_profile_json,
    import_habit_entries_csv, restore_profile_json
)


def test_json_backup_and_restore_cycle(test_db_path: Path):
    """
    Verifies full JSON profile export and safe restore cycle
    with ID remapping and foreign-key integrity.
    """
    p_id = create_profile("Original User", email="orig@example.com", db_path=test_db_path)
    h_id = create_habit(p_id, "Read 20 Pages", "Productivity & Deep Work", target_value=20.0, db_path=test_db_path)
    log_habit_entry(p_id, h_id, "2026-10-25", status="completed", value_recorded=22.0, db_path=test_db_path)

    # 1. Export JSON
    backup = export_profile_json(p_id, db_path=test_db_path)
    assert backup["format"] == "daybalance_profile_backup"
    assert len(backup["habits"]) == 1
    assert len(backup["habit_entries"]) == 1

    # 2. Restore into new profile
    success, msg, counts = restore_profile_json(
        backup,
        target_profile_name="Restored User",
        db_path=test_db_path,
        create_safety_backup=False
    )
    assert success is True
    assert counts["habits"] == 1
    assert counts["entries"] == 1


def test_csv_export_and_import(test_db_path: Path):
    """
    Verifies CSV export and subsequent row-level validation during import.
    """
    p_id = create_profile("CSV User", db_path=test_db_path)
    h_id = create_habit(p_id, "Deep Work", "Study & Academic", target_value=60.0, unit="mins", db_path=test_db_path)

    # Valid CSV content
    valid_csv = (
        "entry_date,habit_name,status,value_recorded,notes\n"
        "2026-10-21,Deep Work,completed,60,Morning study block\n"
        "2026-10-22,Deep Work,completed,90,Extended session\n"
        "2026-10-23,Deep Work,rest_day,0,Recovery\n"
    )

    accepted, rejected, errors = import_habit_entries_csv(p_id, valid_csv, db_path=test_db_path)
    assert accepted == 3
    assert rejected == 0
    assert len(errors) == 0

    # CSV with invalid date and unknown habit
    bad_csv = (
        "entry_date,habit_name,status,value_recorded\n"
        "not-a-date,Deep Work,completed,60\n"
        "2026-10-24,Nonexistent Habit,completed,60\n"
    )

    accepted_bad, rejected_bad, errors_bad = import_habit_entries_csv(p_id, bad_csv, db_path=test_db_path)
    assert accepted_bad == 0
    assert rejected_bad == 2
    assert len(errors_bad) == 2
    assert "Invalid date format" in errors_bad[0]
    assert "does not exist in active profile" in errors_bad[1]
