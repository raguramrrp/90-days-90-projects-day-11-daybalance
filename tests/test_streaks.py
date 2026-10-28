"""
Unit Tests for DayBalance Streaks & Consistency Intelligence
Tests schedule-awareness, rest days, weekend skipping, today's grace period, and historical best streaks.
"""

from datetime import date, timedelta
from services.streaks_service import calculate_habit_streak


def test_basic_daily_streak():
    """Tests contiguous daily completions resulting in an unbroken streak."""
    today = date(2026, 10, 27)  # Tuesday
    start_d = (today - timedelta(days=6)).isoformat()

    habit = {
        "id": 1,
        "start_date": start_d,
        "frequency": "daily",
        "frequency_days_list": [0, 1, 2, 3, 4, 5, 6],
        "is_active": 1
    }

    # 7 contiguous days completed
    entries = {}
    for i in range(7):
        d_str = (today - timedelta(days=i)).isoformat()
        entries[d_str] = {"status": "completed", "value_recorded": 1.0}

    res = calculate_habit_streak(habit, entries, as_of_date=today)
    assert res["current_streak"] == 7
    assert res["best_streak"] == 7
    assert res["completion_rate"] == 100.0
    assert res["is_active"] is True


def test_weekday_habit_does_not_break_over_weekend():
    """
    CRITICAL RULE: A habit scheduled only on weekdays (Mon-Fri) MUST NOT
    lose its streak due to unscheduled weekend days (Sat-Sun).
    """
    # Let Monday be 2026-10-26, Friday was 2026-10-23, Thursday 2026-10-22
    monday = date(2026, 10, 26)  # Monday
    thursday_prior = date(2026, 10, 22)  # Thursday

    habit = {
        "id": 2,
        "start_date": thursday_prior.isoformat(),
        "frequency": "weekdays",
        "frequency_days_list": [0, 1, 2, 3, 4],  # Mon-Fri
        "is_active": 1
    }

    # Completed Thursday (Oct 22), Friday (Oct 23), and Monday (Oct 26).
    # Saturday (Oct 24) and Sunday (Oct 25) were not scheduled and have no entries.
    entries = {
        "2026-10-22": {"status": "completed"},
        "2026-10-23": {"status": "completed"},
        "2026-10-26": {"status": "completed"}
    }

    res = calculate_habit_streak(habit, entries, as_of_date=monday)
    # Total scheduled days: Thu (1), Fri (2), Mon (3) = 3 days
    assert res["current_streak"] == 3
    assert res["best_streak"] == 3
    assert res["completion_rate"] == 100.0
    assert res["is_active"] is True


def test_rest_day_preserves_streak():
    """
    Verifies that an explicitly marked 'rest_day' bridges/preserves
    the active streak without penalizing the user.
    """
    today = date(2026, 10, 27)
    start_d = (today - timedelta(days=4)).isoformat()

    habit = {
        "id": 3,
        "start_date": start_d,
        "frequency": "daily",
        "frequency_days_list": [0, 1, 2, 3, 4, 5, 6],
        "is_active": 1
    }

    # Day -4: completed, Day -3: completed, Day -2: rest_day, Day -1: completed, Day 0: completed
    entries = {
        (today - timedelta(days=4)).isoformat(): {"status": "completed"},
        (today - timedelta(days=3)).isoformat(): {"status": "completed"},
        (today - timedelta(days=2)).isoformat(): {"status": "rest_day"},  # Rest day!
        (today - timedelta(days=1)).isoformat(): {"status": "completed"},
        today.isoformat(): {"status": "completed"}
    }

    res = calculate_habit_streak(habit, entries, as_of_date=today)
    # The 4 completed days form an unbroken streak preserved across the rest day
    assert res["current_streak"] == 4
    assert res["best_streak"] == 4


def test_missed_day_breaks_current_streak_but_preserves_best_streak():
    """
    Verifies that a missed past scheduled day resets the current streak,
    while historical best streak remains preserved.
    """
    today = date(2026, 10, 27)
    start_d = (today - timedelta(days=10)).isoformat()

    habit = {
        "id": 4,
        "start_date": start_d,
        "frequency": "daily",
        "frequency_days_list": [0, 1, 2, 3, 4, 5, 6],
        "is_active": 1
    }

    # Days -10 to -5: completed (6 days)
    # Day -4: missed / skipped
    # Days -3 to 0: completed (4 days)
    entries = {}
    for i in range(5, 11):
        entries[(today - timedelta(days=i)).isoformat()] = {"status": "completed"}
    entries[(today - timedelta(days=4)).isoformat()] = {"status": "skipped"}
    for i in range(4):
        entries[(today - timedelta(days=i)).isoformat()] = {"status": "completed"}

    res = calculate_habit_streak(habit, entries, as_of_date=today)
    assert res["current_streak"] == 4
    assert res["best_streak"] == 6


def test_today_unlogged_grace():
    """
    An unlogged today does not penalize an active streak that was completed yesterday.
    """
    today = date(2026, 10, 27)
    start_d = (today - timedelta(days=5)).isoformat()

    habit = {
        "id": 5,
        "start_date": start_d,
        "frequency": "daily",
        "frequency_days_list": [0, 1, 2, 3, 4, 5, 6],
        "is_active": 1
    }

    # Days -5 to -1 completed. Day 0 (today) is not yet logged!
    entries = {}
    for i in range(1, 6):
        entries[(today - timedelta(days=i)).isoformat()] = {"status": "completed"}

    res = calculate_habit_streak(habit, entries, as_of_date=today)
    # Active streak from yesterday continues
    assert res["current_streak"] == 5
    assert res["is_active"] is True
