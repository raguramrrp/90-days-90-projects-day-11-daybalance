"""
Unit Tests for DayBalance Habit Experiments Service
Validates observational before-and-after calculations, baseline vs intervention slicing, and percent change.
"""

import pandas as pd
from services.experiments_service import evaluate_experiment


def test_experiment_evaluation_math():
    """Verifies baseline vs intervention descriptive statistics and percentage delta."""
    # 20 days of data: days 1-10 study avg = 60 mins, days 11-20 study avg = 120 mins (+100%)
    rows = []
    for i in range(1, 11):
        rows.append({"date": f"2026-10-{i:02d}", "study_minutes": 60})
    for i in range(11, 21):
        rows.append({"date": f"2026-10-{i:02d}", "study_minutes": 120})

    df = pd.DataFrame(rows)

    experiment = {
        "title": "Morning Routine Impact",
        "hypothesis": "Morning routine increases daily study time.",
        "primary_metric": "study_minutes",
        "baseline_start": "2026-10-01",
        "baseline_end": "2026-10-10",
        "intervention_start": "2026-10-11",
        "intervention_end": "2026-10-20"
    }

    res = evaluate_experiment(experiment, df)
    assert res["has_data"] is True
    assert res["baseline_mean"] == 60.0
    assert res["intervention_mean"] == 120.0
    assert res["difference"] == 60.0
    assert res["pct_change"] == 100.0
    assert res["direction"] == "increase"
    assert "Methodological Note" in res["causal_disclaimer"]


def test_experiment_insufficient_data():
    """Verifies graceful handling when date ranges have zero observations."""
    df = pd.DataFrame([{"date": "2026-10-01", "study_minutes": 60}])
    experiment = {
        "primary_metric": "study_minutes",
        "baseline_start": "2026-10-05",
        "baseline_end": "2026-10-10",
        "intervention_start": "2026-10-15",
        "intervention_end": "2026-10-20"
    }
    res = evaluate_experiment(experiment, df)
    assert res["has_data"] is False
    assert "Insufficient logs recorded" in res["message"]
