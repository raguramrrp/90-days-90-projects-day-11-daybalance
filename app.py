"""
DayBalance — Behavioral Habit Analytics & Health Wearable Tracker.
Native Desktop Application Entry Point (Tkinter / Desktop).
Day 11 of the 90 Days : 90 Projects Challenge.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    if "--web" in sys.argv or "--streamlit" in sys.argv:
        # Launch optional Streamlit web interface
        import subprocess
        cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app.py"]
        subprocess.run(cmd)
        return

    # Initialize SQLite database tables
    from database.migrations import init_db
    init_db()

    # Seed demo profile if none exists
    from database.repository import get_profiles
    if not get_profiles():
        from services.demo_data_service import seed_demo_profile
        seed_demo_profile()

    # Launch native desktop application window
    from desktop_app.main_window import MainWindow
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
