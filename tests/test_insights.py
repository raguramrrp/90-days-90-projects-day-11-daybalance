"""
Unit Tests for DayBalance Deterministic Insights Engine
Ensures mathematical triggers fire properly and generate human-readable, actionable guidance.
"""

import pandas as pd
from services.insights_service import generate_behavioral_insights


def test_empty_dataframe_initial_insight():
    """Empty dataframe produces getting-started onboarding insight."""
    insights = generate_behavioral_insights(pd.DataFrame(), [], [])
    assert len(insights) >= 1
    assert insights[0]["category"] == "Getting Started"
    assert "Daily Check-in" in insights[0]["action_step"]


def test_peak_weekday_insight_trigger():
    """Generates peak weekday insight when completion difference is significant (>=15%)."""
    rows = []
    # 2 weeks of logs: Tuesdays 100%, Sundays 40%
    for week in range(2):
        rows.append({"weekday_name": "Tuesday", "completion_rate": 100.0, "sleep_hours": 8.0, "study_minutes": 120, "exercise_minutes": 30, "energy_score": 4})
        rows.append({"weekday_name": "Wednesday", "completion_rate": 80.0, "sleep_hours": 7.5, "study_minutes": 100, "exercise_minutes": 30, "energy_score": 4})
        rows.append({"weekday_name": "Thursday", "completion_rate": 75.0, "sleep_hours": 7.0, "study_minutes": 90, "exercise_minutes": 30, "energy_score": 3})
        rows.append({"weekday_name": "Sunday", "completion_rate": 40.0, "sleep_hours": 7.0, "study_minutes": 50, "exercise_minutes": 0, "energy_score": 2})

    df = pd.DataFrame(rows)
    insights = generate_behavioral_insights(df, [], [])
    peak_insights = [i for i in insights if i["category"] == "Consistency Rhythm"]
    assert len(peak_insights) >= 1
    assert "Tuesday" in peak_insights[0]["title"]
    assert peak_insights[0]["action_step"] != ""


def test_streak_milestone_insight_trigger():
    """Triggers streak milestone when habit current_streak reaches milestone numbers."""
    df = pd.DataFrame([{"completion_rate": 80.0}])
    habit_metrics = [
        {"habit_id": 1, "habit_name": "LeetCode Sprint", "current_streak": 7, "best_streak": 7}
    ]
    insights = generate_behavioral_insights(df, habit_metrics, [])
    milestones = [i for i in insights if i["category"] == "Milestone"]
    assert len(milestones) >= 1
    assert "7-Day" in milestones[0]["title"]
    assert "LeetCode Sprint" in milestones[0]["message"]
