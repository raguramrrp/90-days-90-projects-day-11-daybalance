"""
DayBalance Deterministic Insights Engine
Generates transparent, mathematically verified, rule-based behavioral insights
from actual user logs without black-box or paid external AI APIs.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from config import MIN_CORRELATION_PAIRS, WEEKDAY_NAMES


def generate_behavioral_insights(
    df: pd.DataFrame,
    habit_metrics: List[Dict[str, Any]],
    routines: List[Dict[str, Any]],
    as_of_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates historical data to surface actionable, non-judgmental behavioral insights.
    Only surfaces insights supported by sufficient mathematical evidence.
    """
    insights: List[Dict[str, Any]] = []

    if df.empty:
        insights.append({
            "category": "Getting Started",
            "type": "info",
            "icon": "•",
            "title": "Welcome to DayBalance",
            "message": "Begin by completing your daily check-in. As you record data over the coming days, DayBalance will automatically surface your peak consistency days and lifestyle connections.",
            "metric_proof": "0 logs recorded",
            "caveat": "Insights require at least 3-7 days of genuine daily logs.",
            "action_step": "Head to Daily Check-in and log your habits for today."
        })
        return insights

    logged_days_count = len(df.dropna(subset=["completion_rate"]))

    # 1. Insufficient Data Notice if fewer than 5 days
    if logged_days_count < 5:
        insights.append({
            "category": "Baseline Building",
            "type": "info",
            "icon": "•",
            "title": f"Building Your Baseline ({logged_days_count}/7 Days)",
            "message": f"You have logged {logged_days_count} day(s) so far. Once you reach 7 days, DayBalance will compute weekday consistency curves and rolling performance trends.",
            "metric_proof": f"Sample size n = {logged_days_count} (minimum 7 recommended)",
            "caveat": "Early data may fluctuate widely; early patterns are exploratory.",
            "action_step": "Keep logging consistently for a few more days."
        })

    # 2. Peak Weekday Consistency Analysis (Requires >= 7 days)
    if logged_days_count >= 7:
        day_perf = df.groupby("weekday_name")["completion_rate"].agg(["mean", "count"]).dropna()
        # Only consider weekdays with at least 1 log
        valid_days = day_perf[day_perf["count"] >= 1]
        if len(valid_days) >= 3:
            best_day = valid_days["mean"].idxmax()
            best_rate = valid_days.loc[best_day, "mean"]
            worst_day = valid_days["mean"].idxmin()
            worst_rate = valid_days.loc[worst_day, "mean"]

            if best_rate - worst_rate >= 15.0:
                insights.append({
                    "category": "Consistency Rhythm",
                    "type": "success",
                    "icon": "•",
                    "title": f"Peak Consistency on {best_day}s",
                    "message": f"Your habit completion rate averages **{best_rate:.0f}% on {best_day}s**, compared to **{worst_rate:.0f}% on {worst_day}s**.",
                    "metric_proof": f"Δ = {best_rate - worst_rate:.1f}% spread across {len(valid_days)} weekdays observed",
                    "caveat": "Weekly schedules naturally fluctuate between workdays and weekends.",
                    "action_step": f"Schedule demanding or high-friction habits on {best_day}s when your completion momentum is naturally highest."
                })

    # 3. Active Streak Milestones
    for hm in habit_metrics:
        curr = hm.get("current_streak", 0)
        h_name = hm.get("habit_name", "Habit")
        if curr in (3, 7, 14, 21, 30, 50, 100):
            insights.append({
                "category": "Milestone",
                "type": "success",
                "icon": "🔥",
                "title": f"{curr}-Day Consistency Milestone: {h_name}",
                "message": f"You have completed **{h_name}** for **{curr} consecutive scheduled days**! Consistency compound interest is building.",
                "metric_proof": f"Current streak = {curr} days (Best streak = {hm.get('best_streak', curr)} days)",
                "caveat": "Rest days preserve your streak. Remember that recovery is an intentional part of sustainable performance.",
                "action_step": "Celebrate this milestone without putting undue pressure on tomorrow."
            })

    # 4. Sleep and Study Connection
    if "sleep_hours" in df.columns and "study_minutes" in df.columns:
        sleep_study_valid = df[["sleep_hours", "study_minutes"]].dropna()
        if len(sleep_study_valid) >= MIN_CORRELATION_PAIRS:
            high_sleep = sleep_study_valid[sleep_study_valid["sleep_hours"] >= 7.25]
            low_sleep = sleep_study_valid[sleep_study_valid["sleep_hours"] < 7.0]

            if len(high_sleep) >= 3 and len(low_sleep) >= 3:
                high_study_avg = high_sleep["study_minutes"].mean()
                low_study_avg = low_sleep["study_minutes"].mean()
                diff = high_study_avg - low_study_avg

                if abs(diff) >= 20:
                    direction_word = "more" if diff > 0 else "less"
                    insights.append({
                        "category": "Lifestyle Interplay",
                        "type": "info" if diff > 0 else "warning",
                        "icon": "•",
                        "title": "Sleep Duration & Focus Time Link",
                        "message": f"On days with 7+ hours of sleep, your study/deep work averaged **{high_study_avg:.0f} minutes** vs **{low_study_avg:.0f} minutes** on shorter sleep days ({abs(diff):.0f} mins {direction_word}).",
                        "metric_proof": f"High sleep avg: {high_study_avg:.0f}m (n={len(high_sleep)}) vs Low sleep avg: {low_study_avg:.0f}m (n={len(low_sleep)})",
                        "caveat": "Correlation does not imply causation. Exam schedules or deadlines may shorten sleep while forcing longer study.",
                        "action_step": "Protect a 7-8 hour sleep window to test whether focus quality improves."
                    })

    # 5. Exercise and Energy Boost
    if "exercise_minutes" in df.columns and "energy_score" in df.columns:
        ex_energy_valid = df[["exercise_minutes", "energy_score"]].dropna()
        if len(ex_energy_valid) >= MIN_CORRELATION_PAIRS:
            active_days = ex_energy_valid[ex_energy_valid["exercise_minutes"] >= 20]
            sedentary_days = ex_energy_valid[ex_energy_valid["exercise_minutes"] == 0]

            if len(active_days) >= 3 and len(sedentary_days) >= 3:
                active_energy_avg = active_days["energy_score"].mean()
                sedentary_energy_avg = sedentary_days["energy_score"].mean()
                energy_diff = active_energy_avg - sedentary_energy_avg

                if energy_diff >= 0.4:
                    insights.append({
                        "category": "Energy Vitality",
                        "type": "success",
                        "icon": "•",
                        "title": "Physical Movement Elevates Energy",
                        "message": f"On days with at least 20 minutes of exercise, your self-reported energy averaged **{active_energy_avg:.1f}/5**, compared to **{sedentary_energy_avg:.1f}/5** on rest days.",
                        "metric_proof": f"Energy spread: +{energy_diff:.1f} rating points (active n={len(active_days)}, rest n={len(sedentary_days)})",
                        "caveat": "Self-reported energy can be influenced by subjective mood and caffeine intake.",
                        "action_step": "Even a brief 15-minute walk can serve as a dependable reset when feeling sluggish."
                    })

    # 6. Trend Comparison: Last 7 Days vs Prior 7 Days
    if len(df) >= 14 and "completion_rate" in df.columns:
        recent_7 = df.tail(7)["completion_rate"].dropna()
        prior_7 = df.iloc[-14:-7]["completion_rate"].dropna()

        if len(recent_7) >= 4 and len(prior_7) >= 4:
            r_mean = recent_7.mean()
            p_mean = prior_7.mean()
            delta = r_mean - p_mean

            if delta >= 10.0:
                insights.append({
                    "category": "Momentum Shift",
                    "type": "success",
                    "icon": "•",
                    "title": "Positive Momentum This Week",
                    "message": f"Your completion rate improved by **+{delta:.1f}%** over the last 7 days ({r_mean:.1f}% vs {p_mean:.1f}% in the prior week).",
                    "metric_proof": f"7-day rolling completion: {p_mean:.1f}% → {r_mean:.1f}%",
                    "caveat": "Focus on consistency of effort rather than chasing 100% perfection.",
                    "action_step": "Identify which daily routine supported this improvement."
                })
            elif delta <= -15.0:
                insights.append({
                    "category": "Recovery Opportunity",
                    "type": "warning",
                    "icon": "•",
                    "title": "Slight Dip in Completion Rate",
                    "message": f"Your completion rate decreased by **{abs(delta):.1f}%** compared to the previous week ({r_mean:.1f}% vs {p_mean:.1f}%).",
                    "metric_proof": f"Prior week: {p_mean:.1f}% → Recent week: {r_mean:.1f}%",
                    "caveat": "Lulls in tracking are completely normal and often reflect life events, exams, or fatigue.",
                    "action_step": "Pick just ONE core anchor habit to complete tomorrow to restart momentum without overwhelm."
                })

    return insights
