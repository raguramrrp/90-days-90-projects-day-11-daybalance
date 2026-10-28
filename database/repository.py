"""
DayBalance Data Access Repository
Provides parameterized, transactional, profile-isolated CRUD methods for all entities.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from database.connection import get_db_connection


# ============================================================================
# Profiles
# ============================================================================

def create_profile(
    name: str,
    email: Optional[str] = None,
    theme_preference: str = "dark",
    quiet_hours_start: str = "22:00",
    quiet_hours_end: str = "07:00",
    is_demo: int = 0,
    db_path: Optional[Path] = None
) -> int:
    """Creates a new user profile and returns its profile_id."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO profiles (name, email, theme_preference, quiet_hours_start, quiet_hours_end, is_demo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name.strip(), email.strip() if email else None, theme_preference, quiet_hours_start, quiet_hours_end, is_demo)
        )
        return cursor.lastrowid


def get_profiles(include_archived: bool = False, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Returns a list of all user profiles."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if include_archived:
            cursor.execute("SELECT * FROM profiles ORDER BY created_at ASC")
        else:
            cursor.execute("SELECT * FROM profiles WHERE is_archived = 0 ORDER BY created_at ASC")
        return [dict(row) for row in cursor.fetchall()]


def get_profile_by_id(profile_id: int, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Returns profile details by ID or None."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_profile(
    profile_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    theme_preference: Optional[str] = None,
    quiet_hours_start: Optional[str] = None,
    quiet_hours_end: Optional[str] = None,
    is_archived: Optional[int] = None,
    db_path: Optional[Path] = None
) -> bool:
    """Updates profile attributes."""
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name.strip())
    if email is not None:
        updates.append("email = ?")
        params.append(email.strip() if email else None)
    if theme_preference is not None:
        updates.append("theme_preference = ?")
        params.append(theme_preference)
    if quiet_hours_start is not None:
        updates.append("quiet_hours_start = ?")
        params.append(quiet_hours_start)
    if quiet_hours_end is not None:
        updates.append("quiet_hours_end = ?")
        params.append(quiet_hours_end)
    if is_archived is not None:
        updates.append("is_archived = ?")
        params.append(is_archived)

    if not updates:
        return False

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(profile_id)

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE profiles SET {', '.join(updates)} WHERE id = ?", params)
        return cursor.rowcount > 0


def get_profile_stats_for_deletion(profile_id: int, db_path: Optional[Path] = None) -> Dict[str, int]:
    """Summarizes counts of all dependent entities for safe deletion confirmation."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        counts = {}
        for table, col in [
            ("habits", "profile_id"),
            ("habit_entries", "profile_id"),
            ("routines", "profile_id"),
            ("daily_lifestyle_logs", "profile_id"),
            ("goals", "profile_id"),
            ("habit_experiments", "profile_id"),
            ("focus_sessions", "profile_id")
        ]:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} = ?", (profile_id,))
            counts[table] = cursor.fetchone()[0]
        return counts


def delete_profile(profile_id: int, db_path: Optional[Path] = None) -> bool:
    """Permanently deletes a profile and cascades deletion to all child records."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        return cursor.rowcount > 0


# ============================================================================
# Routines
# ============================================================================

def create_routine(
    profile_id: int,
    name: str,
    time_of_day: str = "morning",
    description: Optional[str] = None,
    order_index: int = 0,
    db_path: Optional[Path] = None
) -> int:
    """Creates a new routine grouping."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO routines (profile_id, name, time_of_day, description, order_index)
            VALUES (?, ?, ?, ?, ?)
            """,
            (profile_id, name.strip(), time_of_day, description.strip() if description else None, order_index)
        )
        return cursor.lastrowid


def get_routines(
    profile_id: int,
    include_inactive: bool = False,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieves routines for a given profile."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM routines WHERE profile_id = ?"
        params: List[Any] = [profile_id]
        if not include_inactive:
            query += " AND is_active = 1"
        query += " ORDER BY order_index ASC, id ASC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def update_routine(
    routine_id: int,
    profile_id: int,
    name: Optional[str] = None,
    time_of_day: Optional[str] = None,
    description: Optional[str] = None,
    order_index: Optional[int] = None,
    is_active: Optional[int] = None,
    db_path: Optional[Path] = None
) -> bool:
    """Updates routine properties."""
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name.strip())
    if time_of_day is not None:
        updates.append("time_of_day = ?")
        params.append(time_of_day)
    if description is not None:
        updates.append("description = ?")
        params.append(description.strip() if description else None)
    if order_index is not None:
        updates.append("order_index = ?")
        params.append(order_index)
    if is_active is not None:
        updates.append("is_active = ?")
        params.append(is_active)

    if not updates:
        return False

    params.extend([routine_id, profile_id])
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE routines SET {', '.join(updates)} WHERE id = ? AND profile_id = ?",
            params
        )
        return cursor.rowcount > 0


def delete_routine(routine_id: int, profile_id: int, db_path: Optional[Path] = None) -> bool:
    """Deletes a routine (habits assigned to it have routine_id set to NULL)."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM routines WHERE id = ? AND profile_id = ?", (routine_id, profile_id))
        return cursor.rowcount > 0


# ============================================================================
# Habits
# ============================================================================

def create_habit(
    profile_id: int,
    name: str,
    category: str,
    measurement_type: str = "boolean",
    target_value: float = 1.0,
    unit: str = "times",
    frequency: str = "daily",
    frequency_days: Optional[List[int]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    reminder_time: Optional[str] = None,
    routine_id: Optional[int] = None,
    color: str = "#0d9488",
    description: Optional[str] = None,
    db_path: Optional[Path] = None
) -> int:
    """Creates a new habit for the profile with validation."""
    if frequency_days is None:
        frequency_days = [0, 1, 2, 3, 4, 5, 6] if frequency == "daily" else [0, 1, 2, 3, 4]

    from datetime import date
    actual_start = start_date or date.today().isoformat()

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO habits (
                profile_id, name, description, category, measurement_type,
                target_value, unit, frequency, frequency_days, start_date,
                end_date, reminder_time, routine_id, color, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                profile_id, name.strip(), description.strip() if description else None,
                category, measurement_type, float(target_value), unit.strip(),
                frequency, json.dumps(frequency_days), actual_start,
                end_date, reminder_time, routine_id, color
            )
        )
        return cursor.lastrowid


def get_habits(
    profile_id: int,
    include_archived: bool = False,
    category: Optional[str] = None,
    routine_id: Optional[int] = None,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieves all habits matching filters for the specified profile."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT h.*, r.name as routine_name FROM habits h LEFT JOIN routines r ON h.routine_id = r.id WHERE h.profile_id = ?"
        params: List[Any] = [profile_id]

        if not include_archived:
            query += " AND h.is_active = 1"
        if category:
            query += " AND h.category = ?"
            params.append(category)
        if routine_id is not None:
            query += " AND h.routine_id = ?"
            params.append(routine_id)

        query += " ORDER BY h.created_at ASC"
        cursor.execute(query, params)
        results = []
        for row in cursor.fetchall():
            d = dict(row)
            d["frequency_days_list"] = json.loads(d["frequency_days"]) if d["frequency_days"] else [0, 1, 2, 3, 4, 5, 6]
            results.append(d)
        return results


def get_habit_by_id(habit_id: int, profile_id: int, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Returns single habit dict by ID or None."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT h.*, r.name as routine_name 
            FROM habits h 
            LEFT JOIN routines r ON h.routine_id = r.id 
            WHERE h.id = ? AND h.profile_id = ?
            """,
            (habit_id, profile_id)
        )
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["frequency_days_list"] = json.loads(d["frequency_days"]) if d["frequency_days"] else [0, 1, 2, 3, 4, 5, 6]
        return d


def update_habit(
    habit_id: int,
    profile_id: int,
    db_path: Optional[Path] = None,
    **fields: Any
) -> bool:
    """Updates habit attributes."""
    allowed = {
        "name", "description", "category", "measurement_type", "target_value",
        "unit", "frequency", "frequency_days", "start_date", "end_date",
        "reminder_time", "routine_id", "color", "is_active", "archived_at"
    }
    updates = []
    params = []
    for k, v in fields.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            if k == "frequency_days" and isinstance(v, list):
                params.append(json.dumps(v))
            elif k == "name" and isinstance(v, str):
                params.append(v.strip())
            else:
                params.append(v)

    if not updates:
        return False

    params.extend([habit_id, profile_id])
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE habits SET {', '.join(updates)} WHERE id = ? AND profile_id = ?",
            params
        )
        return cursor.rowcount > 0


def archive_habit(habit_id: int, profile_id: int, db_path: Optional[Path] = None) -> bool:
    """Marks a habit as archived without deleting historical entries."""
    from datetime import datetime, timezone
    return update_habit(
        habit_id=habit_id,
        profile_id=profile_id,
        is_active=0,
        archived_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        db_path=db_path
    )


def delete_habit(habit_id: int, profile_id: int, db_path: Optional[Path] = None) -> bool:
    """Permanently deletes a habit and associated entries."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habits WHERE id = ? AND profile_id = ?", (habit_id, profile_id))
        return cursor.rowcount > 0


# ============================================================================
# Habit Entries (Daily Habit Logs)
# ============================================================================

def log_habit_entry(
    profile_id: int,
    habit_id: int,
    entry_date: str,
    status: str = "completed",
    value_recorded: float = 1.0,
    target_at_entry: float = 1.0,
    skip_reason: Optional[str] = None,
    notes: Optional[str] = None,
    db_path: Optional[Path] = None
) -> int:
    """
    Records or updates a daily habit entry.
    Preserves target_at_entry at the time of logging to protect historical baseline integrity.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO habit_entries (
                profile_id, habit_id, entry_date, status, value_recorded,
                target_at_entry, skip_reason, notes, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(profile_id, habit_id, entry_date) DO UPDATE SET
                status = excluded.status,
                value_recorded = excluded.value_recorded,
                skip_reason = excluded.skip_reason,
                notes = excluded.notes,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                profile_id, habit_id, entry_date, status,
                float(value_recorded), float(target_at_entry),
                skip_reason.strip() if skip_reason else None,
                notes.strip() if notes else None
            )
        )
        return cursor.lastrowid


def get_habit_entries(
    profile_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    habit_id: Optional[int] = None,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieves habit entries with optional date range and habit filter."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT e.*, h.name as habit_name, h.category, h.measurement_type, h.unit
            FROM habit_entries e
            JOIN habits h ON e.habit_id = h.id
            WHERE e.profile_id = ?
        """
        params: List[Any] = [profile_id]

        if start_date:
            query += " AND e.entry_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND e.entry_date <= ?"
            params.append(end_date)
        if habit_id is not None:
            query += " AND e.habit_id = ?"
            params.append(habit_id)

        query += " ORDER BY e.entry_date ASC, h.name ASC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_daily_habit_entries_map(
    profile_id: int,
    date_str: str,
    db_path: Optional[Path] = None
) -> Dict[int, Dict[str, Any]]:
    """Returns a lookup dict {habit_id: entry_dict} for a specific calendar date."""
    entries = get_habit_entries(profile_id, start_date=date_str, end_date=date_str, db_path=db_path)
    return {e["habit_id"]: e for e in entries}


def delete_habit_entry(
    profile_id: int,
    habit_id: int,
    entry_date: str,
    db_path: Optional[Path] = None
) -> bool:
    """Removes a specific habit entry."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM habit_entries WHERE profile_id = ? AND habit_id = ? AND entry_date = ?",
            (profile_id, habit_id, entry_date)
        )
        return cursor.rowcount > 0


# ============================================================================
# Daily Lifestyle Logs (Sleep, Study, Exercise, Mood, Energy)
# ============================================================================

def log_lifestyle(
    profile_id: int,
    log_date: str,
    sleep_hours: Optional[float] = None,
    sleep_quality: Optional[int] = None,
    study_minutes: Optional[int] = None,
    focus_sessions_count: int = 0,
    exercise_minutes: Optional[int] = None,
    exercise_type: Optional[str] = None,
    mood_score: Optional[int] = None,
    energy_score: Optional[int] = None,
    reflection_notes: Optional[str] = None,
    db_path: Optional[Path] = None
) -> int:
    """Inserts or updates lifestyle metrics for a given date."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO daily_lifestyle_logs (
                profile_id, log_date, sleep_hours, sleep_quality,
                study_minutes, focus_sessions_count, exercise_minutes,
                exercise_type, mood_score, energy_score, reflection_notes, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(profile_id, log_date) DO UPDATE SET
                sleep_hours = COALESCE(excluded.sleep_hours, daily_lifestyle_logs.sleep_hours),
                sleep_quality = COALESCE(excluded.sleep_quality, daily_lifestyle_logs.sleep_quality),
                study_minutes = COALESCE(excluded.study_minutes, daily_lifestyle_logs.study_minutes),
                focus_sessions_count = COALESCE(excluded.focus_sessions_count, daily_lifestyle_logs.focus_sessions_count),
                exercise_minutes = COALESCE(excluded.exercise_minutes, daily_lifestyle_logs.exercise_minutes),
                exercise_type = COALESCE(excluded.exercise_type, daily_lifestyle_logs.exercise_type),
                mood_score = COALESCE(excluded.mood_score, daily_lifestyle_logs.mood_score),
                energy_score = COALESCE(excluded.energy_score, daily_lifestyle_logs.energy_score),
                reflection_notes = COALESCE(excluded.reflection_notes, daily_lifestyle_logs.reflection_notes),
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                profile_id, log_date,
                float(sleep_hours) if sleep_hours is not None else None,
                int(sleep_quality) if sleep_quality is not None else None,
                int(study_minutes) if study_minutes is not None else None,
                int(focus_sessions_count),
                int(exercise_minutes) if exercise_minutes is not None else None,
                exercise_type.strip() if exercise_type else None,
                int(mood_score) if mood_score is not None else None,
                int(energy_score) if energy_score is not None else None,
                reflection_notes.strip() if reflection_notes else None
            )
        )
        return cursor.lastrowid


def get_lifestyle_log(
    profile_id: int,
    log_date: str,
    db_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """Retrieves lifestyle metrics for a single date."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM daily_lifestyle_logs WHERE profile_id = ? AND log_date = ?",
            (profile_id, log_date)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_lifestyle_logs(
    profile_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieves lifestyle logs within a date range."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM daily_lifestyle_logs WHERE profile_id = ?"
        params: List[Any] = [profile_id]

        if start_date:
            query += " AND log_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND log_date <= ?"
            params.append(end_date)

        query += " ORDER BY log_date ASC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# Goals & Milestones
# ============================================================================

def create_goal(
    profile_id: int,
    title: str,
    target_metric: str,
    target_value: float,
    period_type: str = "weekly",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    habit_id: Optional[int] = None,
    db_path: Optional[Path] = None
) -> int:
    """Creates a new progress goal."""
    from datetime import date
    actual_start = start_date or date.today().isoformat()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO goals (
                profile_id, habit_id, title, target_metric, target_value,
                period_type, start_date, end_date, is_achieved, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 1)
            """,
            (
                profile_id, habit_id, title.strip(), target_metric,
                float(target_value), period_type, actual_start, end_date
            )
        )
        return cursor.lastrowid


def get_goals(
    profile_id: int,
    include_inactive: bool = False,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieves goals for a profile."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT g.*, h.name as habit_name
            FROM goals g
            LEFT JOIN habits h ON g.habit_id = h.id
            WHERE g.profile_id = ?
        """
        params: List[Any] = [profile_id]
        if not include_inactive:
            query += " AND g.is_active = 1"
        query += " ORDER BY g.created_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def update_goal(
    goal_id: int,
    profile_id: int,
    db_path: Optional[Path] = None,
    **fields: Any
) -> bool:
    """Updates goal fields."""
    allowed = {"title", "target_metric", "target_value", "period_type", "end_date", "is_achieved", "is_active"}
    updates = []
    params = []
    for k, v in fields.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            params.append(v)
    if not updates:
        return False
    params.extend([goal_id, profile_id])
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE goals SET {', '.join(updates)} WHERE id = ? AND profile_id = ?", params)
        return cursor.rowcount > 0


def delete_goal(goal_id: int, profile_id: int, db_path: Optional[Path] = None) -> bool:
    """Deletes a goal."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ? AND profile_id = ?", (goal_id, profile_id))
        return cursor.rowcount > 0


# ============================================================================
# Habit Experiments
# ============================================================================

def create_experiment(
    profile_id: int,
    title: str,
    hypothesis: str,
    primary_metric: str,
    baseline_start: str,
    baseline_end: str,
    intervention_start: str,
    intervention_end: str,
    habit_id: Optional[int] = None,
    db_path: Optional[Path] = None
) -> int:
    """Creates a structured habit experiment."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO habit_experiments (
                profile_id, title, hypothesis, primary_metric, habit_id,
                baseline_start, baseline_end, intervention_start, intervention_end, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """,
            (
                profile_id, title.strip(), hypothesis.strip(), primary_metric, habit_id,
                baseline_start, baseline_end, intervention_start, intervention_end
            )
        )
        return cursor.lastrowid


def get_experiments(
    profile_id: int,
    status: Optional[str] = None,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieves experiments for a profile."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT exp.*, h.name as habit_name
            FROM habit_experiments exp
            LEFT JOIN habits h ON exp.habit_id = h.id
            WHERE exp.profile_id = ?
        """
        params: List[Any] = [profile_id]
        if status:
            query += " AND exp.status = ?"
            params.append(status)
        query += " ORDER BY exp.created_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def update_experiment(
    experiment_id: int,
    profile_id: int,
    db_path: Optional[Path] = None,
    **fields: Any
) -> bool:
    """Updates experiment status or conclusion notes."""
    allowed = {"title", "hypothesis", "primary_metric", "status", "conclusion_notes"}
    updates = []
    params = []
    for k, v in fields.items():
        if k in allowed:
            updates.append(f"{k} = ?")
            params.append(v)
    if not updates:
        return False
    params.extend([experiment_id, profile_id])
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE habit_experiments SET {', '.join(updates)} WHERE id = ? AND profile_id = ?", params)
        return cursor.rowcount > 0


def delete_experiment(experiment_id: int, profile_id: int, db_path: Optional[Path] = None) -> bool:
    """Deletes an experiment."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM habit_experiments WHERE id = ? AND profile_id = ?", (experiment_id, profile_id))
        return cursor.rowcount > 0


# ============================================================================
# Focus Sessions
# ============================================================================

def create_focus_session(
    profile_id: int,
    task_name: str,
    duration_minutes: int,
    habit_id: Optional[int] = None,
    notes: Optional[str] = None,
    completed_at: Optional[str] = None,
    db_path: Optional[Path] = None
) -> int:
    """Logs a completed focus / study timer session."""
    from datetime import datetime, timezone
    actual_completed = completed_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO focus_sessions (profile_id, habit_id, task_name, duration_minutes, completed_at, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                profile_id, habit_id, task_name.strip(), int(duration_minutes),
                actual_completed, notes.strip() if notes else None
            )
        )
        return cursor.lastrowid


def get_focus_sessions(
    profile_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieves focus sessions within a date range."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT fs.*, h.name as habit_name
            FROM focus_sessions fs
            LEFT JOIN habits h ON fs.habit_id = h.id
            WHERE fs.profile_id = ?
        """
        params: List[Any] = [profile_id]
        if start_date:
            query += " AND date(fs.completed_at) >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date(fs.completed_at) <= ?"
            params.append(end_date)
        query += " ORDER BY fs.completed_at DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


# ============================================================================
# Wearable Devices & Health Biometrics
# ============================================================================

def add_wearable_device(
    profile_id: int,
    device_name: str,
    device_type: str = "smartwatch",
    device_brand: str = "Samsung",
    device_model: Optional[str] = None,
    mac_address: Optional[str] = None,
    battery_level: int = 85,
    is_connected: int = 1,
    db_path: Optional[Path] = None
) -> int:
    """Pairs/registers a new wearable health tracker device."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO wearable_devices (
                profile_id, device_name, device_type, device_brand,
                device_model, mac_address, battery_level, is_connected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile_id, device_name.strip(), device_type.strip(),
                device_brand.strip(), device_model, mac_address,
                int(battery_level), int(is_connected)
            )
        )
        return cursor.lastrowid


def get_wearable_devices(
    profile_id: int,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieves all paired wearable devices for a profile."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM wearable_devices WHERE profile_id = ? ORDER BY created_at DESC",
            (profile_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_wearable_device(
    device_id: int,
    profile_id: int,
    db_path: Optional[Path] = None
) -> bool:
    """Unpairs/removes a wearable device."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM wearable_devices WHERE id = ? AND profile_id = ?",
            (device_id, profile_id)
        )
        return cursor.rowcount > 0


def log_health_biometrics(
    profile_id: int,
    log_date: str,
    resting_hr: Optional[int] = None,
    peak_hr: Optional[int] = None,
    avg_hr: Optional[int] = None,
    bp_systolic: Optional[int] = None,
    bp_diastolic: Optional[int] = None,
    spo2_pct: Optional[int] = None,
    hrv_ms: Optional[int] = None,
    deep_sleep_minutes: Optional[int] = None,
    rem_sleep_minutes: Optional[int] = None,
    light_sleep_minutes: Optional[int] = None,
    sleep_score: Optional[int] = None,
    steps_count: Optional[int] = None,
    active_calories: Optional[int] = None,
    device_id: Optional[int] = None,
    db_path: Optional[Path] = None
) -> int:
    """Inserts or updates daily health biometrics from wearable sync or manual entry."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO health_biometrics (
                profile_id, log_date, device_id, resting_hr, peak_hr, avg_hr,
                bp_systolic, bp_diastolic, spo2_pct, hrv_ms,
                deep_sleep_minutes, rem_sleep_minutes, light_sleep_minutes,
                sleep_score, steps_count, active_calories
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(profile_id, log_date) DO UPDATE SET
                device_id = COALESCE(excluded.device_id, health_biometrics.device_id),
                resting_hr = COALESCE(excluded.resting_hr, health_biometrics.resting_hr),
                peak_hr = COALESCE(excluded.peak_hr, health_biometrics.peak_hr),
                avg_hr = COALESCE(excluded.avg_hr, health_biometrics.avg_hr),
                bp_systolic = COALESCE(excluded.bp_systolic, health_biometrics.bp_systolic),
                bp_diastolic = COALESCE(excluded.bp_diastolic, health_biometrics.bp_diastolic),
                spo2_pct = COALESCE(excluded.spo2_pct, health_biometrics.spo2_pct),
                hrv_ms = COALESCE(excluded.hrv_ms, health_biometrics.hrv_ms),
                deep_sleep_minutes = COALESCE(excluded.deep_sleep_minutes, health_biometrics.deep_sleep_minutes),
                rem_sleep_minutes = COALESCE(excluded.rem_sleep_minutes, health_biometrics.rem_sleep_minutes),
                light_sleep_minutes = COALESCE(excluded.light_sleep_minutes, health_biometrics.light_sleep_minutes),
                sleep_score = COALESCE(excluded.sleep_score, health_biometrics.sleep_score),
                steps_count = COALESCE(excluded.steps_count, health_biometrics.steps_count),
                active_calories = COALESCE(excluded.active_calories, health_biometrics.active_calories)
            """,
            (
                profile_id, log_date, device_id, resting_hr, peak_hr, avg_hr,
                bp_systolic, bp_diastolic, spo2_pct, hrv_ms,
                deep_sleep_minutes, rem_sleep_minutes, light_sleep_minutes,
                sleep_score, steps_count, active_calories
            )
        )
        return cursor.lastrowid


def get_health_biometrics(
    profile_id: int,
    log_date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """Retrieves health biometrics within a date range or for a specific date."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM health_biometrics WHERE profile_id = ?"
        params: List[Any] = [profile_id]
        if log_date:
            query += " AND log_date = ?"
            params.append(log_date)
        if start_date:
            query += " AND log_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND log_date <= ?"
            params.append(end_date)
        query += " ORDER BY log_date DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_latest_health_biometrics(
    profile_id: int,
    db_path: Optional[Path] = None
) -> Optional[Dict[str, Any]]:
    """Retrieves the most recent health biometrics entry for a profile."""
    records = get_health_biometrics(profile_id, db_path=db_path)
    return records[0] if records else None
