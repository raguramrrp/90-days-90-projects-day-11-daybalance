"""
DayBalance — Behavioral Habit Analytics & Consistency Intelligence Dashboard
Streamlit Web application entry point featuring top navigation & editorial wellness design.
"""

import sys
from pathlib import Path
import streamlit as st

# Ensure repository root is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

st.set_page_config(
    page_title="DayBalance | Habit Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Top Navigation Definition with st.Page (clean typography, no emoji bloat)
pages = [
    st.Page("pages/1_Dashboard.py", title="Dashboard", default=True),
    st.Page("pages/2_Daily_Checkin.py", title="Daily Check-in"),
    st.Page("pages/3_Habits_and_Routines.py", title="Habits & Routines"),
    st.Page("pages/4_Calendar_and_History.py", title="Calendar & History"),
    st.Page("pages/5_Analytics_and_Insights.py", title="Analytics & Insights"),
    st.Page("pages/6_Goals_and_Experiments.py", title="Goals & Experiments"),
    st.Page("pages/7_Focus_Timer.py", title="Focus Timer"),
    st.Page("pages/8_Health_and_Wearables.py", title="Health & Wearables"),
    st.Page("pages/9_Settings_and_Profiles.py", title="Settings & Profiles")
]

pg = st.navigation(pages, position="top")
pg.run()
