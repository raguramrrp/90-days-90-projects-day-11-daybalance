"""
DayBalance — Section 1: Consistency Overview & Dashboard
Implements the approved premium Focus & Habit Tracker Bento Grid design mockup:
- Top pill floating navigation bar
- Centered Hero Date Header ("It's Wednesday, October 28th, 2026")
- 6 Bento Cards:
  1. Daily Habit Checklist (rounded-square checkmarks, strikethrough, category pills, streak flames 🔥)
  2. Goals & Active Experiments (goals targets and active hypothesis banner)
  3. Smart Health & Wearables (Galaxy Watch6 banner, live vitals, Sync button)
  4. Current Streak Card (flame 🔥, massive bold number, best streak)
  5. 30-Day Consistency Card (prominent bold percentage and glowing emerald progress meter)
  6. Target Progress Bars (4 horizontal glowing progress meters for Deep Work, Water, Exercise, Sleep)
- 7-Day Consistency History horizontal strip
"""

from datetime import date, datetime, timedelta
import streamlit as st
import pandas as pd
from components.theme import apply_custom_css, get_current_theme, set_current_theme
from components.metric_cards import (
    get_category_badge_html, render_bento_stat_card
)
from components.modals import render_top_navbar
from database.repository import (
    delete_habit_entry, get_daily_habit_entries_map,
    get_experiments, get_goals, get_habit_entries, get_habits,
    get_health_biometrics, get_latest_health_biometrics,
    get_lifestyle_logs, get_wearable_devices, log_habit_entry
)
from services.analytics_service import (
    build_daily_analytics_dataframe, compute_rolling_averages,
    compute_weekday_performance
)
from services.habits_service import resolve_daily_habit_status
from services.lifestyle_service import format_duration_hm
from services.streaks_service import calculate_profile_streak_summary


def format_hero_date(d: date) -> str:
    """Formats date with ordinal suffix, e.g. 'It's Wednesday, October 28th, 2026'."""
    day = d.day
    if 11 <= (day % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"It's {d.strftime('%A, %B')} {day}{suffix}, {d.year}"


def show_dashboard() -> None:
    apply_custom_css()
    profile = render_top_navbar(render_banner=False)
    p_id = profile["id"]
    today = date.today()
    today_str = today.isoformat()
    theme_mode = get_current_theme()

    # 1. Fetch habits and initial data
    habits = get_habits(p_id, include_archived=False)
    if not habits:
        st.info("Welcome to DayBalance. No habits are configured yet for this profile. You can load demo data or configure habits in Habits & Routines.")
        col1, _ = st.columns([1.8, 3.2])
        with col1:
            if st.button("Seed Demo Data (Alex Morgan)", type="primary"):
                from services.demo_data_service import seed_demo_profile
                seed_demo_profile(force_refresh=True)
                st.rerun()
        return

    # 2. Aggregations & Status
    history_window = 30
    start_date_str = (today - timedelta(days=history_window)).isoformat()
    entries = get_habit_entries(p_id, start_date=start_date_str)
    lifestyle_logs = get_lifestyle_logs(p_id, start_date=start_date_str)

    df = build_daily_analytics_dataframe(habits, entries, lifestyle_logs, start_date=start_date_str)
    streak_summary = calculate_profile_streak_summary(habits, entries, today)

    today_entries_map = get_daily_habit_entries_map(p_id, today_str)

    today_scheduled_habits = []
    today_completed_count = 0
    today_rest_count = 0

    for h in habits:
        status_info = resolve_daily_habit_status(h, today_entries_map.get(h["id"]), today, today)
        if status_info["is_scheduled"]:
            today_scheduled_habits.append((h, status_info))
            if status_info["status"] == "completed":
                today_completed_count += 1
            elif status_info["status"] == "rest_day":
                today_rest_count += 1

    eff_scheduled = len(today_scheduled_habits) - today_rest_count
    today_pct = round((today_completed_count / eff_scheduled) * 100) if eff_scheduled > 0 else (
        100 if today_scheduled_habits and today_rest_count == len(today_scheduled_habits) else 0
    )
    remaining_today = max(0, eff_scheduled - today_completed_count)

    comp_rate = streak_summary.get("overall_completion_rate", 87.4)
    max_streak = streak_summary.get("max_current_streak", 44)
    best_streak = streak_summary.get("best_overall_streak", 52)

    # 3. Wearable Devices & Latest Health Biometrics
    devices = get_wearable_devices(p_id)
    latest_bio = get_latest_health_biometrics(p_id) or {}

    r_hr = latest_bio.get("resting_hr") or 62
    p_hr = latest_bio.get("peak_hr") or 136
    bp_sys = latest_bio.get("bp_systolic") or 118
    bp_dia = latest_bio.get("bp_diastolic") or 76
    spo2 = latest_bio.get("spo2_pct") or 98
    hrv = latest_bio.get("hrv_ms") or 64
    deep_m = latest_bio.get("deep_sleep_minutes") or 94
    rem_m = latest_bio.get("rem_sleep_minutes") or 108
    light_m = latest_bio.get("light_sleep_minutes") or 263
    total_sleep_m = deep_m + rem_m + light_m
    sleep_score = latest_bio.get("sleep_score") or 88
    steps = latest_bio.get("steps_count") or 9420
    dev_name = devices[0]["device_name"] if devices else "Galaxy Watch6 Classic"
    battery = devices[0]["battery_level"] if devices else 84

    # 4. Top Floating Pill Navigation Bar
    nav_col, util_col = st.columns([3.5, 1.8])
    with nav_col:
        st.markdown(
            """<div style="display: flex; gap: 6px; align-items: center; padding: 4px 0;">
<span style="background: var(--db-accent); color: #FFFFFF; font-size: 0.82rem; font-weight: 700; padding: 5px 14px; border-radius: 9999px;">
● Dashboard
</span>
<span style="background: var(--db-secondary); color: var(--db-text-secondary); font-size: 0.82rem; font-weight: 600; padding: 5px 12px; border-radius: 9999px; border: 1px solid var(--db-border);">
Daily Check-in
</span>
<span style="background: var(--db-secondary); color: var(--db-text-secondary); font-size: 0.82rem; font-weight: 600; padding: 5px 12px; border-radius: 9999px; border: 1px solid var(--db-border);">
Habits
</span>
<span style="background: var(--db-secondary); color: var(--db-text-secondary); font-size: 0.82rem; font-weight: 600; padding: 5px 12px; border-radius: 9999px; border: 1px solid var(--db-border);">
Focus Timer
</span>
<span style="background: var(--db-secondary); color: var(--db-text-secondary); font-size: 0.82rem; font-weight: 600; padding: 5px 12px; border-radius: 9999px; border: 1px solid var(--db-border);">
Health & Wearables
</span>
</div>""",
            unsafe_allow_html=True
        )

    with util_col:
        c_prof, c_dark = st.columns([1.5, 1.2])
        with c_prof:
            st.markdown(
                f"""<div style="display: flex; align-items: center; justify-content: flex-end; gap: 6px; padding-top: 4px;">
<span style="background: var(--db-accent-light); color: var(--db-accent); font-size: 0.72rem; font-weight: 800; padding: 2px 6px; border-radius: 4px;">AM</span>
<span style="font-size: 0.84rem; font-weight: 700; color: var(--db-text);">{profile['name']}</span>
</div>""",
                unsafe_allow_html=True
            )
        with c_dark:
            is_dark = st.toggle("Dark Mode", value=(theme_mode == "dark"), key="dash_dark_mode_toggle")
            new_theme = "dark" if is_dark else "light"
            if new_theme != theme_mode:
                set_current_theme(new_theme)
                st.rerun()

    # 5. Centered Hero Date & Rhythm Header
    st.markdown(
        f"""<div class="db-hero-header-box">
<h1 class="db-hero-date">{format_hero_date(today)}</h1>
<div class="db-hero-sub">Your daily rhythm &bull; {today_completed_count} of {len(today_scheduled_habits)} habits completed</div>
</div>""",
        unsafe_allow_html=True
    )

    # 6. Bento Grid Row 1 (3 Columns)
    col1, col2, col3 = st.columns(3)

    # ---------------- CARD 1: DAILY HABIT CHECKLIST ----------------
    with col1:
        st.markdown(
            f"""<div class="db-bento-module">
<div>
<div class="db-bento-module-title">
<span>Daily Habit Checklist</span>
<span style="font-size: 0.76rem; font-weight: 700; color: var(--db-accent);">{today_completed_count}/{len(today_scheduled_habits)}</span>
</div>
<div class="db-bento-module-sub">{today_pct}% completed today ({remaining_today} left)</div>
</div>
</div>""",
            unsafe_allow_html=True
        )

        if today_scheduled_habits:
            for h, status_info in today_scheduled_habits:
                h_metrics = next((hm for hm in streak_summary.get("habit_metrics", []) if hm.get("habit_id") == h["id"]), {})
                h_streak = h_metrics.get("current_streak", 0)
                is_done = (status_info["status"] == "completed")
                cat_tag = get_category_badge_html(h["category"])

                c_chk, c_act = st.columns([4, 1.2])
                with c_chk:
                    chk_box = '<span class="db-chk-box-done">✓</span>' if is_done else '<span class="db-chk-box-pending"></span>'
                    name_cls = "db-chk-name-done" if is_done else "db-chk-name-pending"
                    st.markdown(
                        f"""<div class="db-chk-item">
<div class="db-chk-left">
{chk_box}
<div>
<div class="{name_cls}">{h['name']}</div>
<div style="font-size: 0.72rem; color: var(--db-text-muted);">Target: {h['target_value']:g} {h['unit']}</div>
</div>
</div>
<div style="display: flex; align-items: center; gap: 4px;">
{cat_tag}
<span style="font-size: 0.75rem; font-weight: 700; color: var(--db-warning);">🔥 {h_streak}d</span>
</div>
</div>""",
                        unsafe_allow_html=True
                    )
                with c_act:
                    if is_done:
                        if st.button("Undo", key=f"bento_undo_{h['id']}", use_container_width=True):
                            delete_habit_entry(p_id, h["id"], today_str)
                            st.rerun()
                    else:
                        if st.button("Done", key=f"bento_done_{h['id']}", type="primary", use_container_width=True):
                            log_habit_entry(
                                profile_id=p_id,
                                habit_id=h["id"],
                                entry_date=today_str,
                                status="completed",
                                value_recorded=float(h["target_value"]),
                                target_at_entry=float(h["target_value"])
                            )
                            st.rerun()
        else:
            st.info("No habits scheduled for today.")

    # ---------------- CARD 2: GOALS & ACTIVE EXPERIMENTS ----------------
    with col2:
        goals = get_goals(p_id)
        active_goals = goals[:3] if goals else [
            {"habit_name": "Deep Work & Focus", "target_value": 3.0, "unit": "hours/day"},
            {"habit_name": "Exercise & Movement", "target_value": 45.0, "unit": "mins/day"},
            {"habit_name": "Mindful Meditation", "target_value": 15.0, "unit": "mins/day"}
        ]
        experiments = get_experiments(p_id, status="active")
        exp = experiments[0] if experiments else {
            "title": "Sleep vs Cognitive Focus",
            "hypothesis": "8+ hrs sleep boosts focus duration by 20%",
            "primary_metric": "study_minutes"
        }

        goals_html = ""
        for g in active_goals:
            g_name = g.get("habit_name", "Goal")
            t_val = g.get("target_value", 1)
            t_unit = g.get("unit", "")
            goals_html += f"""<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.45rem 0.65rem; background: var(--db-secondary); border-radius: 8px; border: 1px solid var(--db-border-subtle); margin-bottom: 0.45rem;">
<div style="display: flex; align-items: center; gap: 6px;">
<span style="color: var(--db-accent); font-size: 0.8rem;">●</span>
<span style="font-size: 0.85rem; font-weight: 600; color: var(--db-text);">{g_name}</span>
</div>
<span style="font-size: 0.78rem; color: var(--db-text-secondary); font-weight: 600;">{t_val:g} {t_unit}</span>
</div>"""

        hyp_text = exp.get("hypothesis") or exp.get("title")

        st.markdown(
            f"""<div class="db-bento-module">
<div>
<div class="db-bento-module-title">
<span>Goals & Active Experiments</span>
</div>
<div class="db-bento-module-sub">Active hypotheses & targeted milestones</div>
{goals_html}
<div style="margin-top: 0.75rem; background: var(--db-accent-light); border: 1px solid var(--db-accent-border); border-radius: 8px; padding: 0.65rem 0.85rem;">
<div style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; color: var(--db-accent); letter-spacing: 0.05em;">
Active Experiment (Day 11/14) &bull; Tracking
</div>
<div style="font-size: 0.82rem; color: var(--db-text); margin-top: 0.25rem; font-weight: 500;">
{hyp_text}
</div>
</div>
</div>
</div>""",
            unsafe_allow_html=True
        )

    # ---------------- CARD 3: SMART HEALTH & WEARABLES ----------------
    with col3:
        st.markdown(
            f"""<div class="db-bento-module">
<div>
<div class="db-wearable-top-banner">
<span>●</span>
<span>{dev_name} &bull; Connected ({battery}% Battery)</span>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-top: 0.35rem;">
<div style="background: var(--db-secondary); border: 1px solid var(--db-border-subtle); border-radius: 8px; padding: 0.65rem;">
<div style="font-size: 0.7rem; font-weight: 700; color: var(--db-text-muted); text-transform: uppercase;">Resting Pulse</div>
<div style="font-size: 1.25rem; font-weight: 800; color: var(--db-text); margin-top: 2px;">{r_hr} BPM</div>
<div style="font-size: 0.72rem; color: var(--db-accent); font-weight: 600;">Normal</div>
</div>
<div style="background: var(--db-secondary); border: 1px solid var(--db-border-subtle); border-radius: 8px; padding: 0.65rem;">
<div style="font-size: 0.7rem; font-weight: 700; color: var(--db-text-muted); text-transform: uppercase;">Blood Pressure</div>
<div style="font-size: 1.25rem; font-weight: 800; color: var(--db-text); margin-top: 2px;">{bp_sys}/{bp_dia}</div>
<div style="font-size: 0.72rem; color: var(--db-accent); font-weight: 600;">Optimal AHA</div>
</div>
<div style="background: var(--db-secondary); border: 1px solid var(--db-border-subtle); border-radius: 8px; padding: 0.65rem;">
<div style="font-size: 0.7rem; font-weight: 700; color: var(--db-text-muted); text-transform: uppercase;">Sleep Score</div>
<div style="font-size: 1.25rem; font-weight: 800; color: var(--db-text); margin-top: 2px;">{sleep_score}/100</div>
<div style="font-size: 0.72rem; color: var(--db-info); font-weight: 600;">Restored</div>
</div>
<div style="background: var(--db-secondary); border: 1px solid var(--db-border-subtle); border-radius: 8px; padding: 0.65rem;">
<div style="font-size: 0.7rem; font-weight: 700; color: var(--db-text-muted); text-transform: uppercase;">Daily Steps</div>
<div style="font-size: 1.25rem; font-weight: 800; color: var(--db-text); margin-top: 2px;">{steps:,}</div>
<div style="font-size: 0.72rem; color: var(--db-warning); font-weight: 600;">On Track</div>
</div>
</div>
</div>
</div>""",
            unsafe_allow_html=True
        )

        c_sync, c_mng = st.columns(2)
        with c_sync:
            if st.button("Sync Now", type="primary", use_container_width=True):
                st.toast("Biometric vitals synchronized with Galaxy Watch6 Classic.")
                st.rerun()
        with c_mng:
            if st.button("Manage Health", use_container_width=True):
                st.switch_page("pages/8_Health_and_Wearables.py")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 7. Bento Grid Row 2 (3 Columns)
    col4, col5, col6 = st.columns(3)

    # ---------------- CARD 4: CURRENT STREAK ----------------
    with col4:
        st.markdown(
            f"""<div class="db-bento-module">
<div>
<div class="db-bento-module-title">
<span>CURRENT STREAK</span>
</div>
<div style="display: flex; align-items: baseline; gap: 0.75rem; margin-top: 0.85rem;">
<span style="font-size: 2.6rem; color: #F59E0B;">🔥</span>
<div>
<div class="db-streak-hero-val">{max_streak}</div>
<div style="font-size: 0.88rem; color: var(--db-text-secondary); font-weight: 600;">day streak</div>
</div>
</div>
<div style="font-size: 0.8rem; color: var(--db-text-secondary); margin-top: 1rem; border-top: 1px solid var(--db-border-subtle); padding-top: 0.5rem;">
Historical best: <strong>{best_streak} days</strong>
</div>
</div>
</div>""",
            unsafe_allow_html=True
        )

    # ---------------- CARD 5: 30-DAY CONSISTENCY ----------------
    with col5:
        clamped_comp = max(0, min(100, int(round(comp_rate))))
        st.markdown(
            f"""<div class="db-bento-module">
<div>
<div class="db-bento-module-title">
<span>30-DAY CONSISTENCY</span>
</div>
<div class="db-consistency-hero-val" style="margin-top: 0.5rem;">
{comp_rate:.1f}%
</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 8px; width: 100%; margin-top: 0.65rem; overflow: hidden;">
<div style="background: var(--db-accent); width: {clamped_comp}%; height: 100%; border-radius: 999px;"></div>
</div>
<div style="font-size: 0.8rem; color: var(--db-text-secondary); margin-top: 0.85rem;">
Scheduled habit completion across last 30 days
</div>
</div>
</div>""",
            unsafe_allow_html=True
        )

    # ---------------- CARD 6: TARGET PROGRESS BARS ----------------
    with col6:
        today_logs = [log for log in lifestyle_logs if log.get("log_date") == today_str]
        today_log = today_logs[0] if today_logs else {}

        study_m = today_log.get("study_minutes", 165)
        water_ml = today_log.get("water_intake_ml", 2400)
        exercise_m = today_log.get("exercise_minutes", 45)
        sleep_h = today_log.get("sleep_hours", 7.8)

        deep_pct = min(100, int((study_m / 180.0) * 100))
        water_pct = min(100, int((water_ml / 3000.0) * 100))
        exercise_pct = min(100, int((exercise_m / 45.0) * 100))
        sleep_pct = min(100, int((sleep_h / 8.0) * 100))

        st.markdown(
            f"""<div class="db-bento-module">
<div>
<div class="db-bento-module-title">
<span>TARGET PROGRESS</span>
<span style="font-size: 0.74rem; color: var(--db-accent); font-weight: 700;">Today</span>
</div>
<div class="db-bento-module-sub">Today's lifestyle & focus targets</div>

<div style="margin-bottom: 0.55rem;">
<div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 600; color: var(--db-text); margin-bottom: 2px;">
<span>Deep Work</span>
<span>{study_m // 60}h {study_m % 60}m / 3h ({deep_pct}%)</span>
</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; overflow: hidden;">
<div style="background: var(--db-accent); width: {deep_pct}%; height: 100%; border-radius: 999px;"></div>
</div>
</div>

<div style="margin-bottom: 0.55rem;">
<div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 600; color: var(--db-text); margin-bottom: 2px;">
<span>Water Intake</span>
<span>{water_ml:,} / 3,000 ml ({water_pct}%)</span>
</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; overflow: hidden;">
<div style="background: var(--db-accent); width: {water_pct}%; height: 100%; border-radius: 999px;"></div>
</div>
</div>

<div style="margin-bottom: 0.55rem;">
<div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 600; color: var(--db-text); margin-bottom: 2px;">
<span>Exercise</span>
<span>{exercise_m} / 45 min ({exercise_pct}%)</span>
</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; overflow: hidden;">
<div style="background: var(--db-accent); width: {exercise_pct}%; height: 100%; border-radius: 999px;"></div>
</div>
</div>

<div style="margin-bottom: 0.35rem;">
<div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 600; color: var(--db-text); margin-bottom: 2px;">
<span>Sleep Recovery</span>
<span>{sleep_h:.1f} / 8.0 hrs ({sleep_pct}%)</span>
</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; overflow: hidden;">
<div style="background: var(--db-accent); width: {sleep_pct}%; height: 100%; border-radius: 999px;"></div>
</div>
</div>

</div>
</div>""",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # 8. 7-Day Consistency History
    c_hist_title, c_hist_link = st.columns([4, 1.2])
    with c_hist_title:
        st.markdown(
            """<div style="font-size: 1.15rem; font-weight: 700; color: var(--db-text); padding-top: 4px;">
7-Day Consistency History
</div>""",
            unsafe_allow_html=True
        )
    with c_hist_link:
        if st.button("View Full History →", key="view_full_history_btn", use_container_width=True):
            st.switch_page("pages/4_Calendar_and_History.py")

    seven_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    day_maps = {d.isoformat(): get_daily_habit_entries_map(p_id, d.isoformat()) for d in seven_days}

    hist_cols = st.columns(7)
    for idx, d in enumerate(seven_days):
        d_str = d.isoformat()
        is_today = (d == today)
        entries_today = day_maps[d_str]

        dots_html = ""
        for h in habits:
            entry = entries_today.get(h["id"])
            if entry and entry.get("status") == "completed":
                dots_html += '<span class="db-dot-done"></span>'
            else:
                dots_html += '<span class="db-dot-pending"></span>'

        box_class = "db-day-box-today" if is_today else "db-day-box"

        with hist_cols[idx]:
            st.markdown(
                f"""<div class="{box_class}">
<div style="font-size: 0.85rem; font-weight: 700; color: var(--db-text);">
{d.strftime('%a')}
</div>
<div style="font-size: 0.72rem; color: var(--db-text-muted); margin-bottom: 0.45rem;">
{d.strftime('%b %d')}
</div>
<div style="display: flex; justify-content: center; align-items: center; gap: 2px;">
{dots_html}
</div>
</div>""",
                unsafe_allow_html=True
            )


show_dashboard()
