"""
Habit Experiments Service
Provides statistical before-and-after comparison for personal lifestyle hypotheses.
Calculates baseline vs intervention means, medians, standard deviations, and percentage change.
"""

from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from services.analytics_service import METRIC_DISPLAY_NAMES


def evaluate_experiment(
    experiment: Dict[str, Any],
    df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Evaluates a structured habit experiment by comparing baseline vs intervention date ranges.
    Returns descriptive statistics and honest observational conclusions.
    """
    metric = experiment.get("primary_metric", "study_minutes")
    metric_label = METRIC_DISPLAY_NAMES.get(metric, metric)

    b_start = experiment["baseline_start"]
    b_end = experiment["baseline_end"]
    i_start = experiment["intervention_start"]
    i_end = experiment["intervention_end"]

    if df.empty or metric not in df.columns:
        return {
            "has_data": False,
            "metric": metric,
            "metric_label": metric_label,
            "message": f"No data recorded for metric '{metric_label}'."
        }

    # Slice baseline data
    b_mask = (df["date"] >= b_start) & (df["date"] <= b_end)
    b_series = df.loc[b_mask, metric].dropna()

    # Slice intervention data
    i_mask = (df["date"] >= i_start) & (df["date"] <= i_end)
    i_series = df.loc[i_mask, metric].dropna()

    b_n = len(b_series)
    i_n = len(i_series)

    if b_n == 0 or i_n == 0:
        return {
            "has_data": False,
            "metric": metric,
            "metric_label": metric_label,
            "baseline_n": b_n,
            "intervention_n": i_n,
            "message": f"Insufficient logs recorded. Baseline has {b_n} logs; Intervention has {i_n} logs."
        }

    b_mean = float(b_series.mean())
    b_median = float(b_series.median())
    b_std = float(b_series.std()) if b_n > 1 else 0.0

    i_mean = float(i_series.mean())
    i_median = float(i_series.median())
    i_std = float(i_series.std()) if i_n > 1 else 0.0

    diff = i_mean - b_mean
    pct_change = round((diff / b_mean) * 100.0, 1) if b_mean != 0 else None

    direction = "increase" if diff > 0 else ("decrease" if diff < 0 else "no change")

    narrative = (
        f"During the intervention period ({i_start} to {i_end}), **{metric_label}** "
        f"averaged **{i_mean:.1f}** (median: {i_median:.1f}, std: {i_std:.1f}, n={i_n}), "
        f"compared to **{b_mean:.1f}** (median: {b_median:.1f}, std: {b_std:.1f}, n={b_n}) "
        f"during the baseline period ({b_start} to {b_end}). "
        f"This represents an observed **{abs(diff):.1f} unit {direction}**"
        f"{f' ({pct_change:+g}%)' if pct_change is not None else ''}."
    )

    causal_disclaimer = (
        "**Methodological Note**: This is an observational before-and-after comparison. "
        "External life changes (such as exams, travel, or work sprints) may also contribute to observed changes."
    )

    return {
        "has_data": True,
        "metric": metric,
        "metric_label": metric_label,
        "baseline_n": b_n,
        "baseline_mean": round(b_mean, 2),
        "baseline_median": round(b_median, 2),
        "baseline_std": round(b_std, 2),
        "intervention_n": i_n,
        "intervention_mean": round(i_mean, 2),
        "intervention_median": round(i_median, 2),
        "intervention_std": round(i_std, 2),
        "difference": round(diff, 2),
        "pct_change": pct_change,
        "direction": direction,
        "narrative": narrative,
        "causal_disclaimer": causal_disclaimer
    }
