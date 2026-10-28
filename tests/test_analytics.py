"""
Unit Tests for DayBalance Analytics & Statistical Intelligence
Validates Pearson/Spearman calculations, sample-size safeguards, rolling averages, and weekday grouping.
"""

import numpy as np
import pandas as pd
import pytest
from services.analytics_service import (
    calculate_relationship, compute_rolling_averages,
    compute_weekday_performance
)


def test_sample_size_guard():
    """Verifies that correlation calculations require at least min_pairs observations."""
    # Only 5 paired records (below default 7)
    df = pd.DataFrame({
        "sleep_hours": [7.0, 8.0, 6.5, 7.5, 8.5],
        "study_minutes": [100, 140, 80, 110, 150]
    })

    res = calculate_relationship(df, "sleep_hours", "study_minutes", min_pairs=7)
    assert res["is_sufficient"] is False
    assert res["n_pairs"] == 5
    assert "Insufficient paired observations" in res["message"]


def test_perfect_positive_correlation():
    """Verifies Pearson r and Spearman rho equal +1.0 for linear paired series."""
    df = pd.DataFrame({
        "sleep_hours": [6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0],
        "study_minutes": [60, 75, 90, 105, 120, 135, 150]
    })

    res = calculate_relationship(df, "sleep_hours", "study_minutes", min_pairs=7)
    assert res["is_sufficient"] is True
    assert pytest.approx(res["pearson_r"], 0.001) == 1.0
    assert pytest.approx(res["spearman_rho"], 0.001) == 1.0
    assert res["direction"] == "Positive"
    assert res["strength"] == "Strong"


def test_perfect_negative_correlation():
    """Verifies Pearson r equals -1.0 for inverse linear relationship."""
    df = pd.DataFrame({
        "x": [10, 20, 30, 40, 50, 60, 70],
        "y": [70, 60, 50, 40, 30, 20, 10]
    })

    res = calculate_relationship(df, "x", "y", min_pairs=7)
    assert res["is_sufficient"] is True
    assert pytest.approx(res["pearson_r"], 0.001) == -1.0
    assert pytest.approx(res["spearman_rho"], 0.001) == -1.0
    assert res["direction"] == "Negative"
    assert res["strength"] == "Strong"


def test_constant_variable_zero_variance():
    """Verifies that a constant variable with zero variance does not crash and returns a clear explanation."""
    df = pd.DataFrame({
        "sleep_hours": [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0],
        "study_minutes": [60, 80, 90, 110, 120, 130, 140]
    })

    res = calculate_relationship(df, "sleep_hours", "study_minutes", min_pairs=7)
    assert res["is_sufficient"] is False
    assert "constant" in res["message"].lower()


def test_rolling_averages_calculation():
    """Tests 7-day rolling average calculation over sequential daily records."""
    df = pd.DataFrame({
        "date": [f"2026-10-{i:02d}" for i in range(1, 15)],
        "completion_rate": [50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 100.0, 80.0, 80.0, 90.0, 90.0, 100.0, 100.0, 100.0],
        "study_minutes": [60, 60, 90, 90, 120, 120, 150, 120, 120, 120, 150, 150, 180, 180],
        "sleep_hours": [7.0] * 14,
        "exercise_minutes": [30] * 14
    })

    rolling_df = compute_rolling_averages(df, window=7)
    assert "completion_rate_rolling_7" in rolling_df.columns
    # Check 7th item (first full window 50+60+70+80+90+100+100)/7 = 78.57
    assert pytest.approx(rolling_df.loc[6, "completion_rate_rolling_7"], 0.1) == 78.57
