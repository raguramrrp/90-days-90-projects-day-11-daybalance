"""
DayBalance — Section 7: Focus Timer & Deep Work Sessions
Integrated Pomodoro and deep work block timer that persists completed sessions into study analytics.
"""

from datetime import date, datetime, timedelta, timezone
import streamlit as st
from components.theme import apply_custom_css
from components.metric_cards import render_header
from components.modals import render_top_navbar
from database.repository import (
    create_focus_session, get_focus_sessions, get_habit_entries,
    get_habits, get_lifestyle_log, log_lifestyle
)
from services.lifestyle_service import format_duration_hm
from services.streaks_service import calculate_profile_streak_summary


def show_focus_timer() -> None:
    apply_custom_css()
    profile = render_top_navbar()
    p_id = profile["id"]
    today = date.today()
    today_str = today.isoformat()

    render_header(
        title="Focus Timer & Deep Work Sessions"
    )

    # 1. Fetch data & habits
    habits = get_habits(p_id, include_archived=False)
    study_habits = [
        h for h in habits
        if "study" in h["category"].lower() or "study" in h["name"].lower() or "deep" in h["name"].lower()
    ]
    habit_options = study_habits if study_habits else habits
    habit_names = {h["id"]: h["name"] for h in habit_options}

    # Fetch stats for Bento cards
    existing_life = get_lifestyle_log(p_id, today_str) or {}
    today_study_mins = int(existing_life.get("study_minutes") or 0)
    today_sessions_count = int(existing_life.get("focus_sessions_count") or 0)
    today_focus_str = format_duration_hm(today_study_mins) if today_study_mins > 0 else "0m"

    sessions = get_focus_sessions(p_id, start_date=(today - timedelta(days=14)).isoformat())
    avg_session_mins = int(round(sum(s["duration_minutes"] for s in sessions) / len(sessions))) if sessions else 25

    ninety_days_ago = (today - timedelta(days=90)).isoformat()
    entries = get_habit_entries(p_id, start_date=ninety_days_ago)
    streak_summary = calculate_profile_streak_summary(habits, entries, today)
    max_streak = streak_summary.get("max_current_streak", 0)
    best_streak = streak_summary.get("best_overall_streak", 0)

    # 2. Render Top 4 Bento Overview Cards
    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    with c_b1:
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">TODAY'S FOCUS TIME</span>
<span class="db-stat-badge">Today</span>
</div>
<div class="db-bento-value">{today_focus_str}</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
<div style="background: var(--db-accent); width: {min(100, int((today_study_mins / 120) * 100))}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub" style="margin-top: 6px;">{today_sessions_count} sessions completed today</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
    with c_b2:
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">TOTAL SESSIONS (14D)</span>
<span class="db-stat-badge">Completed</span>
</div>
<div class="db-bento-value">{len(sessions)} Sessions</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
<div style="background: #0284C7; width: {min(100, len(sessions) * 10)}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub" style="margin-top: 6px;">Logged in last two weeks</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
    with c_b3:
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">AVERAGE BLOCK</span>
<span class="db-stat-badge">Flow Length</span>
</div>
<div class="db-bento-value">{avg_session_mins} Mins</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
<div style="background: #059669; width: {min(100, int((avg_session_mins / 60) * 100))}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub" style="margin-top: 6px;">Average immersion duration</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
    with c_b4:
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">FOCUS STREAK</span>
<span class="db-stat-badge">Record</span>
</div>
<div class="db-bento-value">{max_streak} Days 🔥</div>
<div style="height: 6px; width: 100%; margin-top: 6px;"></div>
<div class="db-bento-sub" style="margin-top: 6px;">Best all-time streak: {best_streak} days</div>
</div>
</div>""",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # 3. Initialize timer session state
    if "timer_state" not in st.session_state:
        st.session_state["timer_state"] = "stopped"
    if "timer_duration_mins" not in st.session_state:
        st.session_state["timer_duration_mins"] = 25
    if "timer_elapsed_seconds" not in st.session_state:
        st.session_state["timer_elapsed_seconds"] = 0
    if "timer_start_time" not in st.session_state:
        st.session_state["timer_start_time"] = None
    if "timer_task_name" not in st.session_state:
        st.session_state["timer_task_name"] = "Deep Study Block"
    if "timer_habit_id" not in st.session_state:
        st.session_state["timer_habit_id"] = habit_options[0]["id"] if habit_options else None
    if "timer_preset_choice" not in st.session_state:
        st.session_state["timer_preset_choice"] = 25

    # 4. Timer Layout: Left = Session Configuration, Right = Samsung One UI Circular Timer
    col_cfg, col_clock = st.columns([1.1, 1.9])

    with col_cfg:
        st.markdown("#### Session Parameters")
        st.caption("Configure your next uninterrupted deep work block.")

        task_label = st.text_input("Task / Session Goal", value=st.session_state["timer_task_name"])
        st.session_state["timer_task_name"] = task_label

        assigned_habit = st.selectbox(
            "Associate with Habit (Optional)",
            options=[None] + [h["id"] for h in habit_options],
            format_func=lambda x: "None (General Focus)" if x is None else habit_names.get(x, f"Habit #{x}")
        )
        st.session_state["timer_habit_id"] = assigned_habit

        # Duration Presets
        st.markdown("<div style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: var(--db-text-muted); margin: 0.8rem 0 0.4rem 0;'>SELECT DURATION PRESET</div>", unsafe_allow_html=True)

        preset_cols = st.columns(4)
        active_preset = st.session_state["timer_preset_choice"]

        with preset_cols[0]:
            btn_t = "primary" if active_preset == 25 else "secondary"
            if st.button("25m\nPomodoro", key="p_25", type=btn_t, use_container_width=True):
                st.session_state["timer_preset_choice"] = 25
                if st.session_state["timer_state"] == "stopped":
                    st.session_state["timer_duration_mins"] = 25
                st.rerun()

        with preset_cols[1]:
            btn_t = "primary" if active_preset == 45 else "secondary"
            if st.button("45m\nDeep Work", key="p_45", type=btn_t, use_container_width=True):
                st.session_state["timer_preset_choice"] = 45
                if st.session_state["timer_state"] == "stopped":
                    st.session_state["timer_duration_mins"] = 45
                st.rerun()

        with preset_cols[2]:
            btn_t = "primary" if active_preset == 60 else "secondary"
            if st.button("60m\nPower Flow", key="p_60", type=btn_t, use_container_width=True):
                st.session_state["timer_preset_choice"] = 60
                if st.session_state["timer_state"] == "stopped":
                    st.session_state["timer_duration_mins"] = 60
                st.rerun()

        with preset_cols[3]:
            btn_t = "primary" if active_preset == "Custom" else "secondary"
            if st.button("Custom\nSlider", key="p_custom", type=btn_t, use_container_width=True):
                st.session_state["timer_preset_choice"] = "Custom"
                st.rerun()

        if active_preset == "Custom":
            custom_mins = st.slider(
                "Custom Interval (Minutes)",
                min_value=5,
                max_value=180,
                value=int(st.session_state.get("timer_duration_mins", 30)) if isinstance(st.session_state.get("timer_duration_mins"), int) else 30,
                step=5
            )
            if st.session_state["timer_state"] == "stopped":
                st.session_state["timer_duration_mins"] = custom_mins

    # 5. Right Column: Samsung One UI Circular Clock Timer
    with col_clock:
        total_seconds = st.session_state["timer_duration_mins"] * 60
        elapsed = st.session_state["timer_elapsed_seconds"]

        # Calculate current elapsed if running
        if st.session_state["timer_state"] == "running" and st.session_state["timer_start_time"]:
            delta = (datetime.now(timezone.utc) - st.session_state["timer_start_time"]).total_seconds()
            effective_elapsed = min(total_seconds, elapsed + delta)
        else:
            effective_elapsed = elapsed

        remaining_seconds = max(0, int(total_seconds - effective_elapsed))
        rem_min = remaining_seconds // 60
        rem_sec = remaining_seconds % 60
        clock_str = f"{rem_min:02d}:{rem_sec:02d}"

        rem_frac = (remaining_seconds / total_seconds) if total_seconds > 0 else 0.0
        # Circumference for r=115 is 2 * pi * 115 = 722.57
        circumference = 722.57
        dash_offset = circumference * (1.0 - rem_frac)

        st.markdown(
            f"""<div class="db-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 1.8rem 1.4rem; text-align: center; margin-bottom: 0.75rem;">
<div style="position: relative; width: 270px; height: 270px; margin: 0.4rem auto 1.2rem auto;">
<svg width="270" height="270" viewBox="0 0 270 270" style="transform: rotate(-90deg); display: block;">
<circle cx="135" cy="135" r="115" fill="none" stroke="var(--db-border-subtle)" stroke-width="10" />
<circle cx="135" cy="135" r="115" fill="none" stroke="var(--db-accent)" stroke-width="10" stroke-linecap="round" stroke-dasharray="722.57" stroke-dashoffset="{dash_offset:.2f}" style="transition: stroke-dashoffset 0.4s ease;" />
</svg>
<div style="position: absolute; top: 0; left: 0; width: 270px; height: 270px; display: flex; flex-direction: column; align-items: center; justify-content: center; pointer-events: none;">
<div style="font-size: 3.8rem; font-weight: 700; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; letter-spacing: -0.02em; color: var(--db-text); line-height: 1;">
{clock_str}
</div>
<div style="font-size: 0.88rem; font-weight: 600; color: var(--db-text-muted); margin-top: 0.4rem; max-width: 210px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
{st.session_state['timer_task_name']}
</div>
</div>
</div>
<div style="font-size: 0.86rem; color: var(--db-text-secondary); margin-bottom: 0.25rem;">
<span>{int(effective_elapsed // 60)}m Elapsed</span> &bull; <span>{rem_min}m {rem_sec}s Remaining</span>
</div>
</div>""",
            unsafe_allow_html=True
        )

        # Samsung One UI Style Pill Actions Row
        t_state = st.session_state["timer_state"]

        if t_state == "stopped":
            c_s1, c_s2 = st.columns([2, 1])
            with c_s1:
                if st.button("Start Flow", type="primary", use_container_width=True):
                    st.session_state["timer_state"] = "running"
                    st.session_state["timer_start_time"] = datetime.now(timezone.utc)
                    st.rerun()
            with c_s2:
                if st.button("Reset", use_container_width=True):
                    st.session_state["timer_state"] = "stopped"
                    st.session_state["timer_elapsed_seconds"] = 0
                    st.session_state["timer_start_time"] = None
                    st.rerun()

        elif t_state == "running":
            c_r1, c_r2, c_r3, c_r4 = st.columns([1.2, 1.2, 1.4, 1.0])
            with c_r1:
                if st.button("Pause", type="primary", use_container_width=True):
                    delta = (datetime.now(timezone.utc) - st.session_state["timer_start_time"]).total_seconds()
                    st.session_state["timer_elapsed_seconds"] += delta
                    st.session_state["timer_state"] = "paused"
                    st.session_state["timer_start_time"] = None
                    st.rerun()
            with c_r2:
                if st.button("Reset", use_container_width=True):
                    st.session_state["timer_state"] = "stopped"
                    st.session_state["timer_elapsed_seconds"] = 0
                    st.session_state["timer_start_time"] = None
                    st.rerun()
            with c_r3:
                can_complete = (effective_elapsed >= 60) or (remaining_seconds == 0)
                if st.button("Finish & Save", disabled=not can_complete, use_container_width=True):
                    actual_minutes = max(1, int(round(effective_elapsed / 60.0)))
                    create_focus_session(
                        profile_id=p_id,
                        task_name=st.session_state["timer_task_name"],
                        duration_minutes=actual_minutes,
                        habit_id=st.session_state["timer_habit_id"],
                        notes=f"Completed {actual_minutes}m block using DayBalance Focus Timer."
                    )
                    existing_life = get_lifestyle_log(p_id, today_str) or {}
                    cur_study = int(existing_life.get("study_minutes") or 0)
                    cur_sessions = int(existing_life.get("focus_sessions_count") or 0)
                    log_lifestyle(
                        profile_id=p_id,
                        log_date=today_str,
                        study_minutes=cur_study + actual_minutes,
                        focus_sessions_count=cur_sessions + 1
                    )
                    st.session_state["timer_state"] = "stopped"
                    st.session_state["timer_elapsed_seconds"] = 0
                    st.session_state["timer_start_time"] = None
                    st.success(f"Saved {actual_minutes}m focus session! Today's study time updated.")
                    st.rerun()
            with c_r4:
                if st.button("Refresh", use_container_width=True):
                    st.rerun()

        elif t_state == "paused":
            c_p1, c_p2, c_p3 = st.columns([1.5, 1.2, 1.5])
            with c_p1:
                if st.button("Resume Flow", type="primary", use_container_width=True):
                    st.session_state["timer_state"] = "running"
                    st.session_state["timer_start_time"] = datetime.now(timezone.utc)
                    st.rerun()
            with c_p2:
                if st.button("Reset", use_container_width=True):
                    st.session_state["timer_state"] = "stopped"
                    st.session_state["timer_elapsed_seconds"] = 0
                    st.session_state["timer_start_time"] = None
                    st.rerun()
            with c_p3:
                can_complete = (effective_elapsed >= 60) or (remaining_seconds == 0)
                if st.button("Finish & Save", disabled=not can_complete, use_container_width=True):
                    actual_minutes = max(1, int(round(effective_elapsed / 60.0)))
                    create_focus_session(
                        profile_id=p_id,
                        task_name=st.session_state["timer_task_name"],
                        duration_minutes=actual_minutes,
                        habit_id=st.session_state["timer_habit_id"],
                        notes=f"Completed {actual_minutes}m block using DayBalance Focus Timer."
                    )
                    existing_life = get_lifestyle_log(p_id, today_str) or {}
                    cur_study = int(existing_life.get("study_minutes") or 0)
                    cur_sessions = int(existing_life.get("focus_sessions_count") or 0)
                    log_lifestyle(
                        profile_id=p_id,
                        log_date=today_str,
                        study_minutes=cur_study + actual_minutes,
                        focus_sessions_count=cur_sessions + 1
                    )
                    st.session_state["timer_state"] = "stopped"
                    st.session_state["timer_elapsed_seconds"] = 0
                    st.session_state["timer_start_time"] = None
                    st.success(f"Saved {actual_minutes}m focus session! Today's study time updated.")
                    st.rerun()

    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # 6. Recent Focus Sessions History
    st.markdown("#### Completed Focus Sessions History")
    st.caption("Deep work blocks recorded over the last 14 days.")

    if not sessions:
        st.info("No focus sessions completed yet. Start a session above to build your study log.")
    else:
        s_rows = []
        for s in sessions:
            dt = s["completed_at"].replace("T", " ")[:16]
            s_rows.append({
                "Completed At": dt,
                "Task": s["task_name"],
                "Duration": format_duration_hm(s["duration_minutes"]),
                "Associated Habit": s.get("habit_name") or "General Focus",
                "Notes": s.get("notes") or ""
            })
        st.dataframe(s_rows, use_container_width=True, hide_index=True)


show_focus_timer()
