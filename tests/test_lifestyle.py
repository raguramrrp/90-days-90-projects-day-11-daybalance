"""
Unit Tests for DayBalance Lifestyle Metrics Service
Validates metric ranges, formatting, and aggregation helpers.
"""

from services.lifestyle_service import (
    format_duration_hm, summarize_lifestyle_logs,
    validate_lifestyle_inputs
)


def test_lifestyle_validation_ranges():
    """Validates acceptable ranges for daily lifestyle inputs."""
    # Valid inputs
    is_valid, errors = validate_lifestyle_inputs(
        sleep_hours=7.5,
        sleep_quality=4,
        study_minutes=120,
        exercise_minutes=30,
        mood_score=4,
        energy_score=4
    )
    assert is_valid is True
    assert len(errors) == 0

    # Invalid inputs
    is_valid_bad, errors_bad = validate_lifestyle_inputs(
        sleep_hours=26.0,  # > 24h
        sleep_quality=6,   # > 5
        study_minutes=2000, # > 1440m
        mood_score=0       # < 1
    )
    assert is_valid_bad is False
    assert len(errors_bad) == 4


def test_format_duration_hm():
    """Verifies duration formatting into human-readable hours and minutes."""
    assert format_duration_hm(0) == "0m"
    assert format_duration_hm(45) == "45m"
    assert format_duration_hm(60) == "1h"
    assert format_duration_hm(125) == "2h 5m"


def test_summarize_lifestyle_logs():
    """Verifies descriptive statistics aggregation across lifestyle logs."""
    logs = [
        {"sleep_hours": 8.0, "sleep_quality": 4, "study_minutes": 120, "exercise_minutes": 30, "mood_score": 4, "energy_score": 4},
        {"sleep_hours": 6.0, "sleep_quality": 2, "study_minutes": 60, "exercise_minutes": 0, "mood_score": 2, "energy_score": 2}
    ]
    summary = summarize_lifestyle_logs(logs)
    assert summary["total_logged_days"] == 2
    assert summary["avg_sleep_hours"] == 7.0
    assert summary["total_study_minutes"] == 180
    assert summary["avg_study_minutes"] == 90.0
    assert summary["total_exercise_minutes"] == 30
    assert summary["avg_mood_score"] == 3.0
    assert summary["avg_energy_score"] == 3.0
