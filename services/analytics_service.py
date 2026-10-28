"""
DayBalance Advanced Analytics & Statistical Intelligence Service
Provides transparent Pearson and Spearman rank correlation calculations,
sample-size thresholds, rolling averages, weekday breakdowns, and honest causal caveats.
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from config import MIN_CORRELATION_PAIRS, WEEKDAY_NAMES, WEEKDAY_SHORT
from services.habits_service import is_habit_scheduled_on_date


METRIC_DISPLAY_NAMES = {
    "completion_rate": "Habit Completion Rate (%)",
    "sleep_hours": "Sleep Duration (Hours)",
    "sleep_quality": "Sleep Quality (1-5)",
    "study_minutes": "Study / Focus Time (Minutes)",
    "exercise_minutes": "Exercise Duration (Minutes)",
    "mood_score": "Mood Rating (1-5)",
    "energy_score": "Energy Rating (1-5)",
    "focus_sessions_count": "Focus Sessions Count"
}


def build_daily_analytics_dataframe(
    habits: List[Dict[str, Any]],
    entries: List[Dict[str, Any]],
    lifestyle_logs: List[Dict[str, Any]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Constructs a unified, date-indexed daily DataFrame containing:
    - Scheduled habits count and completed habits count
    - Habit completion percentage (0.0 to 100.0)
    - Lifestyle metrics (sleep_hours, study_minutes, exercise_minutes, mood_score, energy_score)
    - Weekday index (0=Mon, 6=Sun), weekday name, and weekend flag
    """
    # 1. Determine date bounds
    all_dates_set = set()
    for e in entries:
        all_dates_set.add(e["entry_date"])
    for l in lifestyle_logs:
        all_dates_set.add(l["log_date"])

    if start_date:
        all_dates_set.add(start_date)
    if end_date:
        all_dates_set.add(end_date)

    if not all_dates_set:
        today_str = date.today().isoformat()
        all_dates_set.add(today_str)

    sorted_dates = sorted(list(all_dates_set))
    min_d = datetime.strptime(start_date or sorted_dates[0], "%Y-%m-%d").date()
    max_d = datetime.strptime(end_date or sorted_dates[-1], "%Y-%m-%d").date()

    date_range = [min_d + timedelta(days=i) for i in range((max_d - min_d).days + 1)]

    # 2. Map entries by date and habit_id
    entries_by_date: Dict[str, Dict[int, Dict[str, Any]]] = {}
    for e in entries:
        d = e["entry_date"]
        if d not in entries_by_date:
            entries_by_date[d] = {}
        entries_by_date[d][e["habit_id"]] = e

    # 3. Map lifestyle logs by date
    lifestyle_by_date = {l["log_date"]: l for l in lifestyle_logs}

    # 4. Assemble rows
    rows = []
    for d in date_range:
        d_str = d.isoformat()
        weekday_idx = d.weekday()

        # Evaluate scheduled habits on this date
        scheduled_count = 0
        completed_count = 0
        rest_count = 0

        for h in habits:
            if is_habit_scheduled_on_date(h, d):
                scheduled_count += 1
                entry = entries_by_date.get(d_str, {}).get(h["id"])
                if entry:
                    st = entry.get("status")
                    if st == "completed":
                        completed_count += 1
                    elif st == "rest_day":
                        rest_count += 1

        effective_scheduled = max(scheduled_count - rest_count, 0)
        completion_rate = (
            round((completed_count / effective_scheduled) * 100.0, 1)
            if effective_scheduled > 0 else (100.0 if scheduled_count > 0 and rest_count == scheduled_count else np.nan)
        )

        life = lifestyle_by_date.get(d_str, {})

        rows.append({
            "date": d_str,
            "date_obj": d,
            "weekday_idx": weekday_idx,
            "weekday_name": WEEKDAY_NAMES[weekday_idx],
            "weekday_short": WEEKDAY_SHORT[weekday_idx],
            "is_weekend": 1 if weekday_idx >= 5 else 0,
            "scheduled_habits": scheduled_count,
            "completed_habits": completed_count,
            "rest_habits": rest_count,
            "completion_rate": completion_rate,
            "sleep_hours": life.get("sleep_hours"),
            "sleep_quality": life.get("sleep_quality"),
            "study_minutes": life.get("study_minutes"),
            "focus_sessions_count": life.get("focus_sessions_count", 0),
            "exercise_minutes": life.get("exercise_minutes"),
            "exercise_type": life.get("exercise_type"),
            "mood_score": life.get("mood_score"),
            "energy_score": life.get("energy_score"),
            "reflection_notes": life.get("reflection_notes")
        })

    df = pd.DataFrame(rows)
    # Cast numeric columns
    numeric_cols = [
        "completion_rate", "sleep_hours", "sleep_quality",
        "study_minutes", "exercise_minutes", "mood_score", "energy_score"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def calculate_relationship(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    min_pairs: int = MIN_CORRELATION_PAIRS
) -> Dict[str, Any]:
    """
    Computes Pearson and Spearman rank correlation between two metrics.
    Enforces minimum sample size threshold, handles non-numeric/missing rows,
    and returns plain-language interpretation with explicit causal caveats.
    """
    x_name = METRIC_DISPLAY_NAMES.get(x_col, x_col)
    y_name = METRIC_DISPLAY_NAMES.get(y_col, y_col)

    if df.empty or x_col not in df.columns or y_col not in df.columns:
        return {
            "is_sufficient": False,
            "x_col": x_col,
            "y_col": y_col,
            "x_name": x_name,
            "y_name": y_name,
            "n_pairs": 0,
            "min_required": min_pairs,
            "message": f"No data recorded yet for {x_name} or {y_name}."
        }

    # Filter to valid paired observations
    valid = df[[x_col, y_col]].dropna()
    n_pairs = len(valid)

    if n_pairs < min_pairs:
        return {
            "is_sufficient": False,
            "x_col": x_col,
            "y_col": y_col,
            "x_name": x_name,
            "y_name": y_name,
            "n_pairs": n_pairs,
            "min_required": min_pairs,
            "message": (
                f"Insufficient paired observations ({n_pairs}/{min_pairs} minimum required). "
                f"Log at least {min_pairs - n_pairs} more day(s) recording both {x_name} and {y_name} "
                "to evaluate this relationship reliably."
            )
        }

    x_vals = valid[x_col].values.astype(float)
    y_vals = valid[y_col].values.astype(float)

    # Check for zero variance / constant series
    std_x = np.std(x_vals)
    std_y = np.std(y_vals)

    if std_x == 0 or std_y == 0:
        constant_var = x_name if std_x == 0 else y_name
        return {
            "is_sufficient": False,
            "x_col": x_col,
            "y_col": y_col,
            "x_name": x_name,
            "y_name": y_name,
            "n_pairs": n_pairs,
            "min_required": min_pairs,
            "message": f"Cannot compute correlation: {constant_var} is constant across all {n_pairs} observations."
        }

    # Pearson correlation coefficient
    pearson_r = float(np.corrcoef(x_vals, y_vals)[0, 1])

    # Spearman rank correlation
    rank_x = pd.Series(x_vals).rank(method="average").values
    rank_y = pd.Series(y_vals).rank(method="average").values
    spearman_rho = float(np.corrcoef(rank_x, rank_y)[0, 1])

    # Interpret direction and strength
    abs_r = abs(pearson_r)
    if abs_r >= 0.70:
        strength = "Strong"
    elif abs_r >= 0.40:
        strength = "Moderate"
    elif abs_r >= 0.20:
        strength = "Weak"
    else:
        strength = "Negligible"

    if pearson_r >= 0.15:
        direction = "Positive"
        trend_desc = f"Higher {x_name} tends to coincide with higher {y_name}."
    elif pearson_r <= -0.15:
        direction = "Negative"
        trend_desc = f"Higher {x_name} tends to coincide with lower {y_name}."
    else:
        direction = "Neutral"
        trend_desc = f"No meaningful linear pattern is evident between {x_name} and {y_name}."

    narrative = (
        f"A **{strength.lower()} {direction.lower()} association** (Pearson r = {pearson_r:+.2f}, "
        f"Spearman ρ = {spearman_rho:+.2f}) was observed across **{n_pairs} paired daily logs**. "
        f"{trend_desc}"
    )

    causal_caveat = (
        "**Observation Notice**: Correlation indicates natural co-occurrence, not direct causation. "
        "These observations reflect everyday lifestyle connections and may be influenced by external factors, "
        "schedule demands, or personal energy."
    )

    return {
        "is_sufficient": True,
        "x_col": x_col,
        "y_col": y_col,
        "x_name": x_name,
        "y_name": y_name,
        "n_pairs": n_pairs,
        "min_required": min_pairs,
        "pearson_r": round(pearson_r, 3),
        "spearman_rho": round(spearman_rho, 3),
        "strength": strength,
        "direction": direction,
        "narrative": narrative,
        "causal_caveat": causal_caveat,
        "valid_df": valid
    }


def compute_weekday_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes average habit completion rate and lifestyle metrics grouped by day of week.
    Returns 7 rows (Monday through Sunday).
    """
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby(["weekday_idx", "weekday_name", "weekday_short"], as_index=False).agg(
        total_days=("date", "count"),
        avg_completion_rate=("completion_rate", "mean"),
        avg_study_minutes=("study_minutes", "mean"),
        avg_sleep_hours=("sleep_hours", "mean"),
        avg_exercise_minutes=("exercise_minutes", "mean"),
        avg_mood=("mood_score", "mean"),
        avg_energy=("energy_score", "mean")
    ).sort_values("weekday_idx")

    grouped["avg_completion_rate"] = grouped["avg_completion_rate"].round(1)
    grouped["avg_study_minutes"] = grouped["avg_study_minutes"].round(1)
    grouped["avg_sleep_hours"] = grouped["avg_sleep_hours"].round(2)
    grouped["avg_exercise_minutes"] = grouped["avg_exercise_minutes"].round(1)
    grouped["avg_mood"] = grouped["avg_mood"].round(1)
    grouped["avg_energy"] = grouped["avg_energy"].round(1)

    return grouped


def compute_rolling_averages(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """
    Computes centered or backward rolling averages for time-series smoothing.
    """
    if df.empty:
        return df

    out = df.copy()
    out = out.sort_values("date")
    for col in ["completion_rate", "study_minutes", "sleep_hours", "exercise_minutes"]:
        if col in out.columns:
            out[f"{col}_rolling_{window}"] = out[col].rolling(window=window, min_periods=max(1, window // 2)).mean().round(2)
    return out
