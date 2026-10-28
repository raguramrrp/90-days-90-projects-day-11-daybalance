"""
Streaks & Consistency Intelligence Service
Provides transparent, schedule-aware streak and completion rate algorithms.
Properly handles rest days, unscheduled days, unlogged days, and recovery.
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from services.habits_service import is_habit_scheduled_on_date


def calculate_habit_streak(
    habit: Dict[str, Any],
    entries_by_date: Dict[str, Dict[str, Any]],
    as_of_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Calculates current streak, best historical streak, and completion rate for a habit.

    Rules:
    1. Schedule Awareness: Days where the habit is NOT scheduled (e.g. weekends for a weekday-only habit)
       do NOT break or interrupt a streak.
    2. Rest Days: Explicitly marked 'rest_day' entries preserve the streak without breaking it.
    3. Today's Grace: An unlogged today does not penalize an active streak that was completed yesterday.
    4. Missed Days: A scheduled past day with no entry or marked 'skipped' breaks the streak.
    5. Best Streak: The maximum contiguous sequence of completed scheduled days across all historical records.
    """
    if as_of_date is None:
        as_of_date = date.today()

    start_date_str = habit.get("start_date")
    if not start_date_str:
        return {
            "current_streak": 0,
            "best_streak": 0,
            "total_scheduled": 0,
            "total_completed": 0,
            "completion_rate": 0.0,
            "last_completed_date": None,
            "status": "not_started"
        }

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except ValueError:
        start_date = as_of_date

    if start_date > as_of_date:
        return {
            "current_streak": 0,
            "best_streak": 0,
            "total_scheduled": 0,
            "total_completed": 0,
            "completion_rate": 0.0,
            "last_completed_date": None,
            "status": "upcoming"
        }

    # Generate all days from start_date up to as_of_date
    delta_days = (as_of_date - start_date).days
    all_dates = [start_date + timedelta(days=i) for i in range(delta_days + 1)]

    # Filter to scheduled days
    scheduled_dates = [d for d in all_dates if is_habit_scheduled_on_date(habit, d)]

    if not scheduled_dates:
        return {
            "current_streak": 0,
            "best_streak": 0,
            "total_scheduled": 0,
            "total_completed": 0,
            "completion_rate": 0.0,
            "last_completed_date": None,
            "status": "no_scheduled_days"
        }

    # 1. Calculate historical metrics and Best Streak (chronological forward pass)
    running_streak = 0
    best_streak = 0
    total_completed = 0
    last_completed_date: Optional[str] = None

    for d in scheduled_dates:
        d_str = d.isoformat()
        entry = entries_by_date.get(d_str)

        if entry:
            status = entry.get("status")
            if status == "completed":
                running_streak += 1
                total_completed += 1
                last_completed_date = d_str
                if running_streak > best_streak:
                    best_streak = running_streak
            elif status == "rest_day":
                # Rest days maintain streak integrity without adding to numerical completed count
                continue
            else:
                # partial or skipped breaks the running sequence
                running_streak = 0
        else:
            # If d is today and unlogged, it doesn't break the historical best count
            if d == as_of_date:
                continue
            running_streak = 0

    # 2. Calculate Current Streak (reverse backward pass from as_of_date)
    current_streak = 0
    streak_active = False

    # Check the most recent scheduled date
    latest_scheduled = scheduled_dates[-1]
    latest_str = latest_scheduled.isoformat()
    latest_entry = entries_by_date.get(latest_str)

    start_eval_idx = len(scheduled_dates) - 1

    # If the latest scheduled date is today and unlogged, check if yesterday was active
    if latest_scheduled == as_of_date and (not latest_entry or latest_entry.get("status") not in ("completed", "rest_day")):
        # Look at the previous scheduled day
        start_eval_idx -= 1

    # Walk backwards through scheduled dates
    for i in range(start_eval_idx, -1, -1):
        d = scheduled_dates[i]
        d_str = d.isoformat()
        entry = entries_by_date.get(d_str)

        if not entry:
            # Missing scheduled entry in the past breaks streak
            break

        status = entry.get("status")
        if status == "completed":
            current_streak += 1
            streak_active = True
        elif status == "rest_day":
            # Rest day maintains the streak
            continue
        else:
            # skipped or partial in the past breaks the current streak
            break

    # If today itself was completed, current streak is guaranteed active
    if latest_scheduled == as_of_date and latest_entry and latest_entry.get("status") == "completed":
        streak_active = True

    total_scheduled = len(scheduled_dates)
    completion_rate = round((total_completed / total_scheduled) * 100.0, 1) if total_scheduled > 0 else 0.0

    return {
        "current_streak": current_streak,
        "best_streak": max(best_streak, current_streak),
        "total_scheduled": total_scheduled,
        "total_completed": total_completed,
        "completion_rate": completion_rate,
        "last_completed_date": last_completed_date,
        "is_active": streak_active
    }


def calculate_profile_streak_summary(
    habits: List[Dict[str, Any]],
    all_entries: List[Dict[str, Any]],
    as_of_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Computes aggregated streak and consistency intelligence across all active habits for a profile.
    """
    if as_of_date is None:
        as_of_date = date.today()

    # Index entries by habit_id -> date_str -> entry
    entries_map: Dict[int, Dict[str, Dict[str, Any]]] = {}
    for entry in all_entries:
        h_id = entry["habit_id"]
        d_str = entry["entry_date"]
        if h_id not in entries_map:
            entries_map[h_id] = {}
        entries_map[h_id][d_str] = entry

    habit_metrics = []
    total_sched_all = 0
    total_comp_all = 0
    max_current_streak = 0
    best_overall_streak = 0

    for habit in habits:
        h_entries = entries_map.get(habit["id"], {})
        streak_info = calculate_habit_streak(habit, h_entries, as_of_date)
        habit_metrics.append({
            "habit_id": habit["id"],
            "habit_name": habit["name"],
            "category": habit["category"],
            **streak_info
        })
        total_sched_all += streak_info["total_scheduled"]
        total_comp_all += streak_info["total_completed"]
        if streak_info["current_streak"] > max_current_streak:
            max_current_streak = streak_info["current_streak"]
        if streak_info["best_streak"] > best_overall_streak:
            best_overall_streak = streak_info["best_streak"]

    overall_rate = round((total_comp_all / total_sched_all) * 100.0, 1) if total_sched_all > 0 else 0.0

    return {
        "overall_completion_rate": overall_rate,
        "max_current_streak": max_current_streak,
        "best_overall_streak": best_overall_streak,
        "total_habits": len(habits),
        "habit_metrics": habit_metrics
    }
