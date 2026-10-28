"""
Unit Tests for DayBalance Focus Sessions Persistence
Validates session logging, retrieval, and lifestyle study integration.
"""

from pathlib import Path
from database.repository import create_focus_session, create_profile, get_focus_sessions


def test_focus_session_logging_and_retrieval(test_db_path: Path):
    """Verifies that focus sessions are correctly saved to SQLite and filtered by profile."""
    p_id = create_profile("Timer User", db_path=test_db_path)

    s1_id = create_focus_session(
        profile_id=p_id,
        task_name="Algorithms Deep Work",
        duration_minutes=45,
        notes="Solved 2 graph problems",
        completed_at="2026-10-27T10:30:00",
        db_path=test_db_path
    )
    assert s1_id > 0

    s2_id = create_focus_session(
        profile_id=p_id,
        task_name="System Architecture Design",
        duration_minutes=50,
        completed_at="2026-10-27T14:00:00",
        db_path=test_db_path
    )
    assert s2_id > 0

    sessions = get_focus_sessions(p_id, db_path=test_db_path)
    assert len(sessions) == 2
    assert sessions[0]["duration_minutes"] == 50  # Ordered DESC by completed_at
    assert sessions[1]["duration_minutes"] == 45
