"""
Habits Service
Handles habit scheduling evaluation, daily status resolution, and habit completion calculations.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional


def is_habit_scheduled_on_date(habit: Dict[str, Any], date_obj: date) -> bool:
    """
    Determines if a habit is scheduled on a given calendar date based on:
    1. Habit start_date and optional end_date bounds
    2. Active status
    3. Habit frequency and frequency_days (0=Monday, 6=Sunday)
    """
    if not habit.get("is_active", 1):
        return False

    # Check start date
    start_date_str = habit.get("start_date")
    if start_date_str:
        try:
            start_d = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            if date_obj < start_d:
                return False
        except ValueError:
            pass

    # Check optional end date
    end_date_str = habit.get("end_date")
    if end_date_str:
        try:
            end_d = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if date_obj > end_d:
                return False
        except ValueError:
            pass

    # Check frequency days (0=Mon, 6=Sun)
    freq = habit.get("frequency", "daily")
    weekday = date_obj.weekday()

    if freq == "daily":
        return True
    elif freq == "weekdays":
        return weekday < 5
    elif freq == "weekends":
        return weekday >= 5
    elif freq == "custom_days":
        freq_days = habit.get("frequency_days_list")
        if freq_days is None:
            import json
            raw = habit.get("frequency_days", "[0,1,2,3,4,5,6]")
            freq_days = json.loads(raw) if isinstance(raw, str) else [0, 1, 2, 3, 4, 5, 6]
        return weekday in freq_days

    return True


def resolve_daily_habit_status(
    habit: Dict[str, Any],
    entry: Optional[Dict[str, Any]],
    date_obj: date,
    today_obj: Optional[date] = None
) -> Dict[str, Any]:
    """
    Resolves the human-readable and analytical status of a habit on a specific date.
    Returns dict with keys:
    - status: 'completed' | 'partial' | 'skipped' | 'rest_day' | 'missed' | 'unlogged' | 'not_scheduled'
    - label: Accessible human label with icon/text
    - value: recorded numeric value
    - target: target value at entry or current habit target
    - is_success: bool (whether it counts positively toward completion)
    """
    if today_obj is None:
        today_obj = date.today()

    is_scheduled = is_habit_scheduled_on_date(habit, date_obj)
    target = float(habit.get("target_value", 1.0))

    if not is_scheduled:
        return {
            "status": "not_scheduled",
            "label": "Off Schedule",
            "symbol": "-",
            "badge_class": "status-off",
            "value": 0.0,
            "target": target,
            "is_success": False,
            "is_scheduled": False,
            "skip_reason": None
        }

    if entry is not None:
        raw_status = entry.get("status", "completed")
        val = float(entry.get("value_recorded", 1.0))
        target_at_entry = float(entry.get("target_at_entry", target))
        skip_reason = entry.get("skip_reason")

        if raw_status == "completed":
            return {
                "status": "completed",
                "label": "Completed",
                "symbol": "✓",
                "badge_class": "status-success",
                "value": val,
                "target": target_at_entry,
                "is_success": True,
                "is_scheduled": True,
                "skip_reason": None
            }
        elif raw_status == "partial":
            return {
                "status": "partial",
                "label": f"Partial ({val:g}/{target_at_entry:g})",
                "symbol": "•",
                "badge_class": "status-warning",
                "value": val,
                "target": target_at_entry,
                "is_success": False,
                "is_scheduled": True,
                "skip_reason": None
            }
        elif raw_status == "rest_day":
            return {
                "status": "rest_day",
                "label": "Scheduled Rest Day",
                "symbol": "R",
                "badge_class": "status-rest",
                "value": val,
                "target": target_at_entry,
                "is_success": True,  # Protected/rest
                "is_scheduled": True,
                "skip_reason": skip_reason or "Rest day"
            }
        elif raw_status == "skipped":
            return {
                "status": "skipped",
                "label": f"Skipped: {skip_reason or 'No reason specified'}",
                "symbol": "—",
                "badge_class": "status-skipped",
                "value": 0.0,
                "target": target_at_entry,
                "is_success": False,
                "is_scheduled": True,
                "skip_reason": skip_reason
            }

    # No entry recorded
    if date_obj < today_obj:
        return {
            "status": "missed",
            "label": "Missed (Unlogged)",
            "symbol": "×",
            "badge_class": "status-danger",
            "value": 0.0,
            "target": target,
            "is_success": False,
            "is_scheduled": True,
            "skip_reason": None
        }
    elif date_obj == today_obj:
        return {
            "status": "unlogged",
            "label": "Pending Today",
            "symbol": "•",
            "badge_class": "status-pending",
            "value": 0.0,
            "target": target,
            "is_success": False,
            "is_scheduled": True,
            "skip_reason": None
        }
    else:
        return {
            "status": "upcoming",
            "label": "Upcoming",
            "symbol": "·",
            "badge_class": "status-upcoming",
            "value": 0.0,
            "target": target,
            "is_success": False,
            "is_scheduled": True,
            "skip_reason": None
        }
