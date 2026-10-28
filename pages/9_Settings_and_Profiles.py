"""
DayBalance — Section 9: Settings, Profiles & Local System Preferences
Manage multiple isolated local profiles, quiet hours, demo datasets, and database integrity.
"""

import sqlite3
import streamlit as st
from components.theme import apply_custom_css, get_current_theme, set_current_theme
from components.metric_cards import render_header
from components.modals import render_top_navbar
from config import DB_PATH
from database.migrations import get_current_schema_version
from database.repository import (
    create_profile, delete_profile, get_profile_by_id,
    get_profile_stats_for_deletion, get_profiles, update_profile
)
from services.demo_data_service import DEMO_PROFILE_NAME, seed_demo_profile


def show_settings_and_profiles() -> None:
    apply_custom_css()
    profile = render_top_navbar()
    p_id = profile["id"]
    profiles = get_profiles()

    render_header(
        title="Settings & Local Profile Workspace",
        subtitle=f"Manage multi-user data isolation, quiet hours, and database storage for {profile['name']}."
    )

    tab_profile, tab_manage_profiles, tab_demo, tab_system = st.tabs([
        "Profile Preferences",
        "Multi-Profile Manager",
        "Demo Dataset Tools",
        "System & Privacy Architecture"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Profile Preferences
    # -------------------------------------------------------------------------
    with tab_profile:
        st.markdown(f"#### Edit Preferences for '{profile['name']}'")

        with st.form(key=f"edit_profile_pref_{p_id}"):
            c1, c2 = st.columns(2)
            with c1:
                name_val = st.text_input("Profile Display Name", value=profile["name"])
            with c2:
                email_val = st.text_input("Contact Email (Optional)", value=profile.get("email") or "")

            c3, c4 = st.columns(2)
            with c3:
                cur_pref = profile.get("theme_preference", "light")
                theme_val = st.selectbox(
                    "Default Theme",
                    options=["light", "dark"],
                    index=0 if cur_pref == "light" else 1,
                    format_func=lambda t: "Light Mode (Daybreak)" if t == "light" else "Dark Mode (Obsidian)"
                )
            with c4:
                st.markdown("**Quiet Hours Window**")
                qh_start = st.text_input("Quiet Hours Start", value=profile.get("quiet_hours_start", "22:00"))
                qh_end = st.text_input("Quiet Hours End", value=profile.get("quiet_hours_end", "07:00"))

            save_pref_btn = st.form_submit_button("Save Profile Preferences", type="primary")
            if save_pref_btn:
                update_profile(
                    profile_id=p_id,
                    name=name_val,
                    email=email_val,
                    theme_preference=theme_val,
                    quiet_hours_start=qh_start,
                    quiet_hours_end=qh_end
                )
                set_current_theme(theme_val)
                st.success("✓ Profile preferences saved.")
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: Multi-Profile Manager
    # -------------------------------------------------------------------------
    with tab_manage_profiles:
        st.markdown("#### Local Profiles (Data Isolation)")
        st.caption("Each profile maintains completely independent habits, entries, lifestyle logs, and analytics.")

        # List profiles
        for p in profiles:
            is_active = (p["id"] == p_id)
            active_badge = '<span class="db-target-pill" style="background: rgba(16, 185, 129, 0.12); color: #059669; border-color: #10B981;">Active Profile</span>' if is_active else '<span class="db-target-pill">Inactive</span>'
            demo_badge = '<span class="db-routine-pill">Demo</span>' if p.get('is_demo') else ''

            st.markdown(
                f"""
                <div class="db-checkin-habit-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.15rem; font-weight: 700; color: var(--db-text);">
                            {p['name']}
                        </span>
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            {demo_badge}
                            {active_badge}
                        </div>
                    </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(f"**Profile ID:** `{p['id']}` • Created: `{p['created_at'][:10]}` • Theme: `{p.get('theme_preference', 'light')}`")

            c_p_act1, c_p_act2, _ = st.columns([1.5, 1.5, 3.0])
            with c_p_act1:
                if not is_active:
                    if st.button(f"Switch to '{p['name']}'", key=f"switch_p_{p['id']}", type="primary", use_container_width=True):
                        st.session_state["active_profile_id"] = p["id"]
                        set_current_theme(p.get("theme_preference", "light"))
                        st.rerun()
            with c_p_act2:
                if len(profiles) > 1:
                    with st.popover(f"Delete Profile"):
                        stats = get_profile_stats_for_deletion(p["id"])
                        st.error(f"Permanent deletion of '{p['name']}'")
                        st.markdown(
                            f"""
                            This will permanently erase:
                            - **{stats.get('habits', 0)}** habits
                            - **{stats.get('habit_entries', 0)}** daily habit logs
                            - **{stats.get('daily_lifestyle_logs', 0)}** lifestyle logs
                            - **{stats.get('routines', 0)}** routines
                            - **{stats.get('goals', 0)}** goals
                            - **{stats.get('habit_experiments', 0)}** experiments
                            - **{stats.get('focus_sessions', 0)}** focus sessions
                            """
                        )
                        if st.button("Confirm Delete Profile", key=f"del_p_confirm_{p['id']}", type="primary"):
                            delete_profile(p["id"])
                            remaining = get_profiles()
                            if remaining:
                                st.session_state["active_profile_id"] = remaining[0]["id"]
                            st.success(f"Profile '{p['name']}' deleted.")
                            st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--db-border-subtle);'/>", unsafe_allow_html=True)
        st.markdown("##### + Create New Local Profile")
        with st.form(key="create_new_profile_form"):
            new_p_name = st.text_input("New Profile Name *", placeholder="e.g. Work & Research, Fitness Only")
            new_p_email = st.text_input("Email (Optional)")
            new_p_theme = st.selectbox(
                "Preferred Theme",
                options=["light", "dark"],
                format_func=lambda t: "Light Mode" if t == "light" else "Dark Mode"
            )
            create_p_btn = st.form_submit_button("Create Profile", type="primary")
            if create_p_btn:
                if not new_p_name.strip():
                    st.error("Profile name is required.")
                else:
                    new_id = create_profile(
                        name=new_p_name,
                        email=new_p_email,
                        theme_preference=new_p_theme,
                        is_demo=0
                    )
                    st.session_state["active_profile_id"] = new_id
                    st.success(f"✓ Profile '{new_p_name}' created and activated!")
                    st.rerun()

    # -------------------------------------------------------------------------
    # TAB 3: Demo Dataset Tools
    # -------------------------------------------------------------------------
    with tab_demo:
        st.markdown("#### Illustrative Demo Dataset")
        st.caption("Generate or reset a realistic 60-day portfolio dataset demonstrating correlation, streaks, and routines.")

        st.markdown(
            f"""
            <div class="db-card" style="border-left: 4px solid var(--db-accent);">
                <strong>Demo Persona:</strong> {DEMO_PROFILE_NAME}<br>
                Contains 60 days of realistic daily entries:
                - 6 habits (Deep Study, Morning Exercise, Meditation, Reading, Sleep, Digital Sunset)
                - Morning and evening routines
                - Realistic lifestyle co-variation (sleep ↔ study time, exercise ↔ energy)
                - Active 11-day consistency streak
                - Structured habit experiment and goals
            </div>
            """,
            unsafe_allow_html=True
        )

        c_d1, c_d2 = st.columns(2)
        with c_d1:
            if st.button("Seed / Refresh Demo Profile", type="primary", use_container_width=True):
                demo_id = seed_demo_profile(force_refresh=True)
                st.session_state["active_profile_id"] = demo_id
                st.success("✓ Demo profile generated and set to active!")
                st.rerun()

        with c_d2:
            st.caption("Seeding is deterministic (seed=42), ensuring repeatable results across test runs.")

    # -------------------------------------------------------------------------
    # TAB 4: System & Privacy Architecture
    # -------------------------------------------------------------------------
    with tab_system:
        st.markdown("#### System & Privacy Architecture")
        st.caption("DayBalance is built on local-first principles. Your behavioral data belongs entirely to you.")

        c_s1, c_s2 = st.columns(2)
        with c_s1:
            st.markdown("##### Storage & Data Integrity")
            st.markdown(f"- **Database Path:** `{DB_PATH}`")
            st.markdown(f"- **Schema Version:** `v{get_current_schema_version()}`")
            st.markdown("- **Engine:** SQLite 3 with Write-Ahead Logging (WAL)")
            st.markdown("- **Foreign Keys:** Enforced strictly per-connection (`PRAGMA foreign_keys = ON;`)")
            st.markdown("- **Network Access:** Zero external cloud APIs, tracking, or telemetry.")
        with c_s2:
            st.markdown("##### Analytics Integrity")
            st.markdown("- **Correlations:** Pearson & Spearman computed via standard numerical formulas.")
            st.markdown("- **Causal Stance:** Strict non-causal reporting. No fabricated predictive claims.")
            st.markdown("- **Streaks:** Schedule-aware algorithm respecting rest days and custom frequencies.")


show_settings_and_profiles()
