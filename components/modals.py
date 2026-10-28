"""
DayBalance Top Navigation & Profile State Manager
Handles horizontal top-bar navigation, multi-profile switching, theme toggle, and in-app reminders.
"""

from datetime import date
from typing import Any, Dict, List, Optional
import streamlit as st
from components.theme import get_current_theme, set_current_theme
from database.migrations import init_db
from database.repository import get_habits, get_profiles
from services.demo_data_service import seed_demo_profile
from services.habits_service import is_habit_scheduled_on_date


def initialize_app_state() -> None:
    """Ensures database is initialized and active profile is established in session state."""
    init_db()

    if "active_theme" not in st.session_state:
        st.session_state["active_theme"] = "light"

    profiles = get_profiles()
    if not profiles:
        # Auto-seed demo profile for first run
        demo_id = seed_demo_profile()
        st.session_state["active_profile_id"] = demo_id
    elif "active_profile_id" not in st.session_state or not any(p["id"] == st.session_state["active_profile_id"] for p in profiles):
        st.session_state["active_profile_id"] = profiles[0]["id"]


def get_active_profile() -> Optional[Dict[str, Any]]:
    """Returns the currently active profile dictionary."""
    initialize_app_state()
    active_id = st.session_state.get("active_profile_id")
    profiles = get_profiles()
    for p in profiles:
        if p["id"] == active_id:
            return p
    return profiles[0] if profiles else None


def render_top_navbar(render_banner: bool = True) -> Dict[str, Any]:
    """
    Renders top navigation bar with brand identity and top-corner theme toggle.
    Renders active profile switcher in the sidebar.
    Returns active profile dictionary.
    """
    initialize_app_state()
    profiles = get_profiles()
    active_id = st.session_state.get("active_profile_id", profiles[0]["id"] if profiles else 1)

    # 1. Profile Switcher placed neatly on the side (in the Sidebar)
    with st.sidebar:
        st.markdown(
            """
            <div style="margin-bottom: 0.6rem; padding-bottom: 0.4rem; border-bottom: 1px solid var(--db-border-subtle);">
                <span style="font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--db-text-muted);">
                    Active Profile
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        profile_names = {p["id"]: f"{p['name']}{' (Demo)' if p.get('is_demo') else ''}" for p in profiles}
        id_list = list(profile_names.keys())
        c_idx = id_list.index(active_id) if active_id in id_list else 0
        sel_id = st.selectbox(
            "Select Profile",
            options=id_list,
            index=c_idx,
            format_func=lambda x: profile_names.get(x, f"Profile #{x}"),
            key="sidebar_nav_profile_selector",
            label_visibility="collapsed"
        )
        if sel_id != active_id:
            st.session_state["active_profile_id"] = sel_id
            for p in profiles:
                if p["id"] == sel_id:
                    pref = p.get("theme_preference", "light")
                    set_current_theme(pref)
                    break
            st.rerun()

    active_profile = next((p for p in profiles if p["id"] == sel_id), profiles[0])

    if not render_banner:
        return active_profile

    # 2. Compact Top Navbar: Brand on left, theme toggle in top side corner
    c_brand, c_theme = st.columns([5.2, 1.2])

    with c_brand:
        st.markdown(
            """
            <div style="display: flex; align-items: baseline; gap: 0.6rem; padding-top: 4px;">
                <span style="font-size: 1.3rem; font-weight: 800; color: var(--db-accent); letter-spacing: -0.02em;">DayBalance</span>
                <span style="font-size: 0.78rem; color: var(--db-text-muted); text-transform: uppercase; letter-spacing: 0.05em; border-left: 1px solid var(--db-border); padding-left: 0.5rem;">Habit & Consistency Analytics</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c_theme:
        cur_theme = get_current_theme()
        is_dark = st.toggle("Dark Mode", value=(cur_theme == "dark"), key="top_nav_theme_toggle")
        new_theme = "dark" if is_dark else "light"
        if new_theme != cur_theme:
            set_current_theme(new_theme)
            st.rerun()

    st.markdown("<div style='height: 1px; margin-bottom: 0.75rem; border-bottom: 1px solid var(--db-border-subtle);'></div>", unsafe_allow_html=True)
    return active_profile


def render_sidebar_controls() -> Dict[str, Any]:
    """Compatibility wrapper that routes to the new horizontal top utility bar."""
    return render_top_navbar()
