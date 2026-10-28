"""
Lifestyle Metrics Service
Provides validation, normalization, and descriptive labels for daily lifestyle logs.
(Sleep, Study, Exercise, Mood, and Energy)
"""

from typing import Any, Dict, List, Optional, Tuple


MOOD_LABELS = {
    1: "Very Low",
    2: "Low",
    3: "Neutral",
    4: "Good",
    5: "Great"
}

ENERGY_LABELS = {
    1: "Exhausted",
    2: "Low Energy",
    3: "Moderate",
    4: "Energetic",
    5: "Peak Energy"
}

SLEEP_QUALITY_LABELS = {
    1: "Poor / Restless",
    2: "Fair",
    3: "Average",
    4: "Restful",
    5: "Deep & Refreshing"
}


def validate_lifestyle_inputs(
    sleep_hours: Optional[float] = None,
    sleep_quality: Optional[int] = None,
    study_minutes: Optional[int] = None,
    exercise_minutes: Optional[int] = None,
    mood_score: Optional[int] = None,
    energy_score: Optional[int] = None
) -> Tuple[bool, List[str]]:
    """
    Validates boundary ranges for daily lifestyle metrics.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    if sleep_hours is not None:
        if not (0.0 <= sleep_hours <= 24.0):
            errors.append("Sleep duration must be between 0 and 24 hours.")

    if sleep_quality is not None:
        if sleep_quality not in (1, 2, 3, 4, 5):
            errors.append("Sleep quality must be rated between 1 (Poor) and 5 (Refreshing).")

    if study_minutes is not None:
        if not (0 <= study_minutes <= 1440):
            errors.append("Study / deep work duration must be between 0 and 1440 minutes (24 hours).")

    if exercise_minutes is not None:
        if not (0 <= exercise_minutes <= 1440):
            errors.append("Exercise duration must be between 0 and 1440 minutes.")

    if mood_score is not None:
        if mood_score not in (1, 2, 3, 4, 5):
            errors.append("Mood rating must be between 1 (Very Low) and 5 (Great).")

    if energy_score is not None:
        if energy_score not in (1, 2, 3, 4, 5):
            errors.append("Energy rating must be between 1 (Exhausted) and 5 (Peak Energy).")

    return (len(errors) == 0, errors)


def format_duration_hm(minutes: int) -> str:
    """Formats minutes into human-readable hours and minutes (e.g., 2h 15m)."""
    if minutes <= 0:
        return "0m"
    h = minutes // 60
    m = minutes % 60
    if h > 0 and m > 0:
        return f"{h}h {m}m"
    elif h > 0:
        return f"{h}h"
    return f"{m}m"


def summarize_lifestyle_logs(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregates lifestyle records over a given set of days.
    """
    if not logs:
        return {
            "total_logged_days": 0,
            "avg_sleep_hours": 0.0,
            "avg_sleep_quality": 0.0,
            "total_study_minutes": 0,
            "avg_study_minutes": 0.0,
            "total_exercise_minutes": 0,
            "avg_exercise_minutes": 0.0,
            "avg_mood_score": 0.0,
            "avg_energy_score": 0.0
        }

    sleep_vals = [l["sleep_hours"] for l in logs if l.get("sleep_hours") is not None]
    quality_vals = [l["sleep_quality"] for l in logs if l.get("sleep_quality") is not None]
    study_vals = [l["study_minutes"] for l in logs if l.get("study_minutes") is not None]
    exercise_vals = [l["exercise_minutes"] for l in logs if l.get("exercise_minutes") is not None]
    mood_vals = [l["mood_score"] for l in logs if l.get("mood_score") is not None]
    energy_vals = [l["energy_score"] for l in logs if l.get("energy_score") is not None]

    return {
        "total_logged_days": len(logs),
        "avg_sleep_hours": round(sum(sleep_vals) / len(sleep_vals), 2) if sleep_vals else 0.0,
        "avg_sleep_quality": round(sum(quality_vals) / len(quality_vals), 1) if quality_vals else 0.0,
        "total_study_minutes": sum(study_vals),
        "avg_study_minutes": round(sum(study_vals) / len(study_vals), 1) if study_vals else 0.0,
        "total_exercise_minutes": sum(exercise_vals),
        "avg_exercise_minutes": round(sum(exercise_vals) / len(exercise_vals), 1) if exercise_vals else 0.0,
        "avg_mood_score": round(sum(mood_vals) / len(mood_vals), 1) if mood_vals else 0.0,
        "avg_energy_score": round(sum(energy_vals) / len(energy_vals), 1) if energy_vals else 0.0
    }
