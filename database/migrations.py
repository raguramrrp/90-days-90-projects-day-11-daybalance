"""
DayBalance Database Migration & Initialization Engine
Handles idempotent schema setup and version tracking.
"""

from pathlib import Path
from typing import Optional
from database.connection import get_db_connection
from database.schema import CREATE_TABLES_SQL, SCHEMA_VERSION


def init_db(db_path: Optional[Path] = None) -> None:
    """
    Initializes database tables and verifies schema migration status.
    Safe to execute multiple times (idempotent).
    """
    with get_db_connection(db_path) as conn:
        conn.executescript(CREATE_TABLES_SQL)
        
        # Verify if migration version is recorded
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_migrations WHERE version = ?", (SCHEMA_VERSION,))
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                (SCHEMA_VERSION, "initial_schema_v1")
            )


def get_current_schema_version(db_path: Optional[Path] = None) -> int:
    """Returns the highest applied schema migration version."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(version) FROM schema_migrations")
        row = cursor.fetchone()
        return row[0] if (row and row[0] is not None) else 0
