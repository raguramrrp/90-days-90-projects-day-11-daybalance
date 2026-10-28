"""
DayBalance Database Schema & Table Definitions
Enforces foreign keys, unique constraints, and schema versioning.
"""

SCHEMA_VERSION = 1

CREATE_TABLES_SQL = """
-- Foreign key enforcement is activated per-connection
PRAGMA foreign_keys = ON;

-- 1. User Profiles (Local Multi-Profile Architecture)
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    theme_preference TEXT NOT NULL DEFAULT 'dark',
    quiet_hours_start TEXT NOT NULL DEFAULT '22:00',
    quiet_hours_end TEXT NOT NULL DEFAULT '07:00',
    is_demo INTEGER NOT NULL DEFAULT 0,
    is_archived INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Routines (Morning, Evening, Custom groupings)
CREATE TABLE IF NOT EXISTS routines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    time_of_day TEXT NOT NULL DEFAULT 'morning',
    description TEXT,
    order_index INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

-- 3. Habits (Core Trackable Entities)
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    measurement_type TEXT NOT NULL DEFAULT 'boolean',
    target_value REAL NOT NULL DEFAULT 1.0,
    unit TEXT NOT NULL DEFAULT 'times',
    frequency TEXT NOT NULL DEFAULT 'daily',
    frequency_days TEXT NOT NULL DEFAULT '[0,1,2,3,4,5,6]',
    start_date TEXT NOT NULL,
    end_date TEXT,
    reminder_time TEXT,
    routine_id INTEGER,
    color TEXT NOT NULL DEFAULT '#0d9488',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived_at TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (routine_id) REFERENCES routines(id) ON DELETE SET NULL
);

-- 4. Habit Entries (Daily logs for each habit)
CREATE TABLE IF NOT EXISTS habit_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    habit_id INTEGER NOT NULL,
    entry_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    value_recorded REAL NOT NULL DEFAULT 1.0,
    target_at_entry REAL NOT NULL DEFAULT 1.0,
    skip_reason TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
    UNIQUE(profile_id, habit_id, entry_date)
);

-- 5. Daily Lifestyle Logs (Sleep, Study, Exercise, Mood, Energy)
CREATE TABLE IF NOT EXISTS daily_lifestyle_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    sleep_hours REAL,
    sleep_quality INTEGER,
    study_minutes INTEGER,
    focus_sessions_count INTEGER DEFAULT 0,
    exercise_minutes INTEGER,
    exercise_type TEXT,
    mood_score INTEGER,
    energy_score INTEGER,
    reflection_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    UNIQUE(profile_id, log_date)
);

-- 6. Goals & Milestones
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    habit_id INTEGER,
    title TEXT NOT NULL,
    target_metric TEXT NOT NULL,
    target_value REAL NOT NULL,
    period_type TEXT NOT NULL DEFAULT 'weekly',
    start_date TEXT NOT NULL,
    end_date TEXT,
    is_achieved INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
);

-- 7. Habit Experiments (A/B Lifestyle Hypotheses)
CREATE TABLE IF NOT EXISTS habit_experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    primary_metric TEXT NOT NULL,
    habit_id INTEGER,
    baseline_start TEXT NOT NULL,
    baseline_end TEXT NOT NULL,
    intervention_start TEXT NOT NULL,
    intervention_end TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    conclusion_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE SET NULL
);

-- 8. Focus Sessions (Pomodoro & Deep Work logs)
CREATE TABLE IF NOT EXISTS focus_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    habit_id INTEGER,
    task_name TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE SET NULL
);

-- 9. Schema Migrations Tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Wearable & Smart Health Devices (Smartwatches, Fitness Bands, Smart Rings)
CREATE TABLE IF NOT EXISTS wearable_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    device_name TEXT NOT NULL,
    device_type TEXT NOT NULL DEFAULT 'smartwatch',
    device_brand TEXT NOT NULL,
    device_model TEXT,
    mac_address TEXT,
    is_connected INTEGER NOT NULL DEFAULT 1,
    battery_level INTEGER DEFAULT 85,
    last_sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
);

-- 11. Health Biometrics Log (Heart Rate, Blood Pressure, SpO2, Sleep Stages)
CREATE TABLE IF NOT EXISTS health_biometrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    device_id INTEGER,
    log_date TEXT NOT NULL,
    resting_hr INTEGER,
    peak_hr INTEGER,
    avg_hr INTEGER,
    bp_systolic INTEGER,
    bp_diastolic INTEGER,
    spo2_pct INTEGER,
    hrv_ms INTEGER,
    deep_sleep_minutes INTEGER,
    rem_sleep_minutes INTEGER,
    light_sleep_minutes INTEGER,
    sleep_score INTEGER,
    steps_count INTEGER,
    active_calories INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES wearable_devices(id) ON DELETE SET NULL,
    UNIQUE(profile_id, log_date)
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_habits_profile ON habits(profile_id, is_active);
CREATE INDEX IF NOT EXISTS idx_entries_lookup ON habit_entries(profile_id, entry_date);
CREATE INDEX IF NOT EXISTS idx_entries_habit ON habit_entries(habit_id, entry_date);
CREATE INDEX IF NOT EXISTS idx_lifestyle_lookup ON daily_lifestyle_logs(profile_id, log_date);
CREATE INDEX IF NOT EXISTS idx_focus_profile ON focus_sessions(profile_id, completed_at);
"""
