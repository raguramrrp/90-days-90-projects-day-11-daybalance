"""
DayBalance Backup, Restore & Data Portability Service
Provides complete JSON profile export/restore with ID mapping, automated pre-restore backups,
and CSV import/export with row-level validation.
"""

from datetime import datetime, timezone
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from config import BACKUPS_DIR
from database.connection import get_db_connection
from database.repository import (
    create_habit, create_profile, create_routine,
    get_habits, get_profile_by_id, get_routines, log_habit_entry
)
from database.schema import SCHEMA_VERSION


def export_profile_json(profile_id: int, db_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Exports a comprehensive, self-contained JSON snapshot of a single profile.
    Guarantees strict profile data isolation.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Profile metadata
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        p_row = cursor.fetchone()
        if not p_row:
            raise ValueError(f"Profile {profile_id} not found.")
        profile_data = dict(p_row)

        # 2. Routines
        cursor.execute("SELECT * FROM routines WHERE profile_id = ? ORDER BY order_index, id", (profile_id,))
        routines = [dict(r) for r in cursor.fetchall()]

        # 3. Habits
        cursor.execute("SELECT * FROM habits WHERE profile_id = ? ORDER BY id", (profile_id,))
        habits = [dict(r) for r in cursor.fetchall()]

        # 4. Habit entries
        cursor.execute("SELECT * FROM habit_entries WHERE profile_id = ? ORDER BY entry_date, habit_id", (profile_id,))
        entries = [dict(r) for r in cursor.fetchall()]

        # 5. Lifestyle logs
        cursor.execute("SELECT * FROM daily_lifestyle_logs WHERE profile_id = ? ORDER BY log_date", (profile_id,))
        lifestyle = [dict(r) for r in cursor.fetchall()]

        # 6. Goals
        cursor.execute("SELECT * FROM goals WHERE profile_id = ? ORDER BY id", (profile_id,))
        goals = [dict(r) for r in cursor.fetchall()]

        # 7. Experiments
        cursor.execute("SELECT * FROM habit_experiments WHERE profile_id = ? ORDER BY id", (profile_id,))
        experiments = [dict(r) for r in cursor.fetchall()]

        # 8. Focus sessions
        cursor.execute("SELECT * FROM focus_sessions WHERE profile_id = ? ORDER BY completed_at", (profile_id,))
        sessions = [dict(r) for r in cursor.fetchall()]

    return {
        "format": "daybalance_profile_backup",
        "schema_version": SCHEMA_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "profile": profile_data,
        "routines": routines,
        "habits": habits,
        "habit_entries": entries,
        "daily_lifestyle_logs": lifestyle,
        "goals": goals,
        "habit_experiments": experiments,
        "focus_sessions": sessions
    }


def restore_profile_json(
    backup_data: Dict[str, Any],
    target_profile_name: Optional[str] = None,
    db_path: Optional[Path] = None,
    create_safety_backup: bool = True
) -> Tuple[bool, str, Dict[str, int]]:
    """
    Restores a profile from a valid DayBalance JSON backup.
    Performs pre-restore backup, validates structure, creates a new isolated profile,
    and remaps routine and habit IDs to avoid foreign key collisions.
    """
    if not isinstance(backup_data, dict) or "format" not in backup_data or backup_data.get("format") != "daybalance_profile_backup":
        return False, "Invalid backup file: missing 'daybalance_profile_backup' signature.", {}

    profile_dict = backup_data.get("profile")
    if not profile_dict or "name" not in profile_dict:
        return False, "Invalid backup file: profile metadata missing.", {}

    # Safety: create pre-restore snapshot
    if create_safety_backup:
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        pre_backup_path = BACKUPS_DIR / f"pre_restore_safety_{ts}.json"
        with open(pre_backup_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2)

    new_name = target_profile_name or f"{profile_dict['name']} (Restored)"

    counts = {
        "routines": 0,
        "habits": 0,
        "entries": 0,
        "lifestyle_logs": 0,
        "goals": 0,
        "experiments": 0,
        "focus_sessions": 0
    }

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Create target profile
        cursor.execute(
            """
            INSERT INTO profiles (name, email, theme_preference, quiet_hours_start, quiet_hours_end, is_demo)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                new_name,
                profile_dict.get("email"),
                profile_dict.get("theme_preference", "dark"),
                profile_dict.get("quiet_hours_start", "22:00"),
                profile_dict.get("quiet_hours_end", "07:00"),
                0
            )
        )
        new_profile_id = cursor.lastrowid

        # 2. Restore Routines with ID remapping
        routine_id_map: Dict[int, int] = {}
        for r in backup_data.get("routines", []):
            old_r_id = r["id"]
            cursor.execute(
                """
                INSERT INTO routines (profile_id, name, time_of_day, description, order_index, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (new_profile_id, r["name"], r.get("time_of_day", "morning"), r.get("description"), r.get("order_index", 0), r.get("is_active", 1))
            )
            routine_id_map[old_r_id] = cursor.lastrowid
            counts["routines"] += 1

        # 3. Restore Habits with ID remapping and routine mapping
        habit_id_map: Dict[int, int] = {}
        for h in backup_data.get("habits", []):
            old_h_id = h["id"]
            new_r_id = routine_id_map.get(h.get("routine_id")) if h.get("routine_id") else None
            cursor.execute(
                """
                INSERT INTO habits (
                    profile_id, name, description, category, measurement_type,
                    target_value, unit, frequency, frequency_days, start_date,
                    end_date, reminder_time, routine_id, color, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_profile_id, h["name"], h.get("description"), h.get("category", "Custom"),
                    h.get("measurement_type", "boolean"), float(h.get("target_value", 1.0)),
                    h.get("unit", "times"), h.get("frequency", "daily"),
                    h.get("frequency_days", "[0,1,2,3,4,5,6]"), h["start_date"],
                    h.get("end_date"), h.get("reminder_time"), new_r_id,
                    h.get("color", "#0d9488"), h.get("is_active", 1)
                )
            )
            habit_id_map[old_h_id] = cursor.lastrowid
            counts["habits"] += 1

        # 4. Restore Habit Entries
        for e in backup_data.get("habit_entries", []):
            new_h_id = habit_id_map.get(e["habit_id"])
            if new_h_id:
                cursor.execute(
                    """
                    INSERT INTO habit_entries (
                        profile_id, habit_id, entry_date, status, value_recorded,
                        target_at_entry, skip_reason, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        new_profile_id, new_h_id, e["entry_date"], e.get("status", "completed"),
                        float(e.get("value_recorded", 1.0)), float(e.get("target_at_entry", 1.0)),
                        e.get("skip_reason"), e.get("notes")
                    )
                )
                counts["entries"] += 1

        # 5. Restore Lifestyle Logs
        for l in backup_data.get("daily_lifestyle_logs", []):
            cursor.execute(
                """
                INSERT INTO daily_lifestyle_logs (
                    profile_id, log_date, sleep_hours, sleep_quality, study_minutes,
                    focus_sessions_count, exercise_minutes, exercise_type,
                    mood_score, energy_score, reflection_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_profile_id, l["log_date"], l.get("sleep_hours"), l.get("sleep_quality"),
                    l.get("study_minutes"), l.get("focus_sessions_count", 0),
                    l.get("exercise_minutes"), l.get("exercise_type"),
                    l.get("mood_score"), l.get("energy_score"), l.get("reflection_notes")
                )
            )
            counts["lifestyle_logs"] += 1

        # 6. Restore Goals
        for g in backup_data.get("goals", []):
            new_h_id = habit_id_map.get(g.get("habit_id")) if g.get("habit_id") else None
            cursor.execute(
                """
                INSERT INTO goals (
                    profile_id, habit_id, title, target_metric, target_value,
                    period_type, start_date, end_date, is_achieved, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_profile_id, new_h_id, g["title"], g["target_metric"],
                    float(g["target_value"]), g.get("period_type", "weekly"),
                    g["start_date"], g.get("end_date"), g.get("is_achieved", 0),
                    g.get("is_active", 1)
                )
            )
            counts["goals"] += 1

        # 7. Restore Experiments
        for exp in backup_data.get("habit_experiments", []):
            new_h_id = habit_id_map.get(exp.get("habit_id")) if exp.get("habit_id") else None
            cursor.execute(
                """
                INSERT INTO habit_experiments (
                    profile_id, title, hypothesis, primary_metric, habit_id,
                    baseline_start, baseline_end, intervention_start, intervention_end,
                    status, conclusion_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_profile_id, exp["title"], exp["hypothesis"], exp["primary_metric"],
                    new_h_id, exp["baseline_start"], exp["baseline_end"],
                    exp["intervention_start"], exp["intervention_end"],
                    exp.get("status", "active"), exp.get("conclusion_notes")
                )
            )
            counts["experiments"] += 1

        # 8. Restore Focus Sessions
        for fs in backup_data.get("focus_sessions", []):
            new_h_id = habit_id_map.get(fs.get("habit_id")) if fs.get("habit_id") else None
            cursor.execute(
                """
                INSERT INTO focus_sessions (
                    profile_id, habit_id, task_name, duration_minutes, completed_at, notes
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    new_profile_id, new_h_id, fs["task_name"], int(fs["duration_minutes"]),
                    fs["completed_at"], fs.get("notes")
                )
            )
            counts["focus_sessions"] += 1

    msg = f"Profile '{new_name}' successfully restored with {counts['habits']} habits and {counts['entries']} daily logs."
    return True, msg, counts


def export_habits_csv(profile_id: int, db_path: Optional[Path] = None) -> str:
    """Exports habit definitions for a profile as CSV string."""
    habits = get_habits(profile_id, include_archived=True, db_path=db_path)
    if not habits:
        return "id,name,category,measurement_type,target_value,unit,frequency,start_date,is_active\n"
    df = pd.DataFrame(habits)
    cols = ["id", "name", "category", "measurement_type", "target_value", "unit", "frequency", "start_date", "is_active", "routine_name"]
    cols = [c for c in cols if c in df.columns]
    return df[cols].to_csv(index=False)


def export_entries_csv(
    profile_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db_path: Optional[Path] = None
) -> str:
    """Exports daily habit entries with habit metadata as CSV string."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT e.entry_date, h.name as habit_name, h.category, e.status,
                   e.value_recorded, e.target_at_entry, h.unit, e.skip_reason, e.notes
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
        query += " ORDER BY e.entry_date DESC, h.name ASC"
        cursor.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]

    if not rows:
        return "entry_date,habit_name,category,status,value_recorded,target_at_entry,unit,skip_reason,notes\n"
    return pd.DataFrame(rows).to_csv(index=False)


def import_habit_entries_csv(
    profile_id: int,
    csv_text: str,
    db_path: Optional[Path] = None
) -> Tuple[int, int, List[str]]:
    """
    Imports habit entries from CSV with row-level validation.
    Returns (accepted_count, rejected_count, error_messages).
    """
    try:
        df = pd.read_csv(io.StringIO(csv_text))
    except Exception as e:
        return 0, 0, [f"Failed to parse CSV file: {str(e)}"]

    # Normalize column names
    col_map = {c.lower().strip().replace(" ", "_"): c for c in df.columns}

    date_col = next((col_map[c] for c in ["entry_date", "date", "log_date"] if c in col_map), None)
    habit_col = next((col_map[c] for c in ["habit_name", "habit", "name"] if c in col_map), None)

    if not date_col or not habit_col:
        return 0, 0, ["CSV must contain 'entry_date' (or 'date') and 'habit_name' (or 'habit') columns."]

    status_col = next((col_map[c] for c in ["status", "state"] if c in col_map), None)
    val_col = next((col_map[c] for c in ["value_recorded", "value", "count", "amount"] if c in col_map), None)
    reason_col = next((col_map[c] for c in ["skip_reason", "reason"] if c in col_map), None)
    notes_col = next((col_map[c] for c in ["notes", "note", "reflection"] if c in col_map), None)

    # Fetch active habits for mapping
    existing_habits = {h["name"].lower().strip(): h for h in get_habits(profile_id, include_archived=True, db_path=db_path)}

    accepted = 0
    rejected = 0
    errors: List[str] = []

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        for idx, row in df.iterrows():
            row_num = idx + 2  # 1-indexed header + row
            raw_date = str(row[date_col]).strip()
            raw_habit = str(row[habit_col]).strip()

            # Validate date
            try:
                parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date().isoformat()
            except ValueError:
                rejected += 1
                errors.append(f"Row {row_num}: Invalid date format '{raw_date}' (expected YYYY-MM-DD).")
                continue

            # Resolve habit
            habit_obj = existing_habits.get(raw_habit.lower())
            if not habit_obj:
                rejected += 1
                errors.append(f"Row {row_num}: Habit '{raw_habit}' does not exist in active profile. Create the habit first.")
                continue

            # Resolve status
            raw_status = str(row[status_col]).lower().strip() if status_col and pd.notna(row[status_col]) else "completed"
            if raw_status not in ("completed", "partial", "skipped", "rest_day"):
                raw_status = "completed"

            # Resolve value
            val = float(habit_obj.get("target_value", 1.0))
            if val_col and pd.notna(row[val_col]):
                try:
                    val = float(row[val_col])
                except ValueError:
                    pass

            reason = str(row[reason_col]).strip() if reason_col and pd.notna(row[reason_col]) else None
            notes = str(row[notes_col]).strip() if notes_col and pd.notna(row[notes_col]) else None

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
                    profile_id, habit_obj["id"], parsed_date, raw_status,
                    val, float(habit_obj.get("target_value", 1.0)), reason, notes
                )
            )
            accepted += 1

    return accepted, rejected, errors
