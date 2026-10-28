"""
DayBalance — Section 2: Daily Check-in & Lifestyle Journal
Spacious, attractive, dashboard-style check-in with prominent Bento cards,
generous habit cards, intuitive lifestyle tiles, and zero confusing formulas.
"""

from datetime import date, datetime
import streamlit as st
from components.theme import apply_custom_css, get_current_theme
from components.metric_cards import get_category_badge_html, render_bento_stat_card
from components.modals import render_top_navbar
from database.repository import (
    get_daily_habit_entries_map, get_habits,
    get_lifestyle_log, log_habit_entry, log_lifestyle
)
from services.habits_service import is_habit_scheduled_on_date, resolve_daily_habit_status
from services.lifestyle_service import (
    ENERGY_LABELS, MOOD_LABELS, SLEEP_QUALITY_LABELS,
    format_duration_hm, validate_lifestyle_inputs
)


def show_daily_checkin() -> None:
    apply_custom_css()
    profile = render_top_navbar(render_banner=False)
    p_id = profile["id"]
    today = date.today()

    # 1. Top Date Picker & Header
    c_hdr_left, c_hdr_right = st.columns([3.2, 1.8])

    with c_hdr_right:
        c_date_input, c_status_box = st.columns([1.5, 1.5])
        with c_date_input:
            selected_date = st.date_input(
                "Check-in Date",
                value=today,
                max_value=today,
                key="checkin_date_picker",
                label_visibility="collapsed"
            )
        date_str = selected_date.isoformat()
        habits = get_habits(p_id, include_archived=False)
        existing_entries = get_daily_habit_entries_map(p_id, date_str)
        existing_life = get_lifestyle_log(p_id, date_str) or {}

        scheduled_habits = [h for h in habits if is_habit_scheduled_on_date(h, selected_date)]
        other_habits = [h for h in habits if not is_habit_scheduled_on_date(h, selected_date)]
        completed_count = sum(1 for h in scheduled_habits if existing_entries.get(h["id"], {}).get("status") == "completed")
        remaining_count = max(0, len(scheduled_habits) - completed_count)

        with c_status_box:
            if remaining_count == 0 and scheduled_habits:
                st.markdown(
                    """
                    <div style="text-align: right; padding-top: 6px;">
                        <span style="display: inline-block; background: #DEF7EC; color: #047857; font-size: 0.82rem; font-weight: 700; padding: 5px 14px; border-radius: 9999px;">
                            ✓ All Habits Logged
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="text-align: right; padding-top: 6px;">
                        <span style="display: inline-block; background: #FEF3C7; color: #92400E; font-size: 0.82rem; font-weight: 700; padding: 5px 14px; border-radius: 9999px;">
                            ● {remaining_count} Remaining
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    with c_hdr_left:
        st.markdown(
            f"""
            <div style="margin-bottom: 0.75rem;">
                <h1 style="font-size: 2.1rem; font-weight: 800; color: var(--db-text); margin: 0; line-height: 1.15; letter-spacing: -0.025em;">
                    Daily Habit Check-in & Journal
                </h1>
                <div style="font-size: 0.92rem; color: var(--db-text-secondary); margin-top: 0.35rem;">
                    Active Profile: <strong>{profile['name']} (Demo – Student & Builder)</strong> • {selected_date.strftime('%A, %B %d, %Y')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if not habits:
        st.info("No habits configured yet. Go to 'Habits & Routines' or seed demo data.")
        return

    # 2. Hero Bento Stats Strip (Spacious & Attractive like Dashboard)
    pct = round((completed_count / len(scheduled_habits)) * 100) if scheduled_habits else 0
    sleep_hrs = float(existing_life.get("sleep_hours") or 7.5)
    study_mins = int(existing_life.get("study_minutes") or 120)
    mood_score = int(existing_life.get("mood_score") or 4)
    energy_score = int(existing_life.get("energy_score") or 4)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_bento_stat_card(
            label="TODAY'S HABITS",
            value=f"{completed_count} / {len(scheduled_habits)}",
            subtext=f"{pct}% complete ({remaining_count} left)" if remaining_count > 0 else "All habits completed for today",
            icon=None
        )
    with col2:
        render_bento_stat_card(
            label="DEEP FOCUS LOGGED",
            value=format_duration_hm(study_mins),
            subtext=f"{existing_life.get('focus_sessions_count', 2)} focus blocks recorded",
            icon=None
        )
    with col3:
        sq_val = int(existing_life.get("sleep_quality", 4))
        render_bento_stat_card(
            label="SLEEP & NIGHTLY REST",
            value=f"{sleep_hrs:g} Hours",
            subtext=f"Quality: {SLEEP_QUALITY_LABELS.get(sq_val, 'Restful')}",
            icon=None
        )
    with col4:
        render_bento_stat_card(
            label="DAILY ENERGY & MOOD",
            value=f"{ENERGY_LABELS.get(energy_score, 'High Energy')}",
            subtext=f"Mood: {MOOD_LABELS.get(mood_score, 'Good Mood')}",
            icon=None
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. Main Check-in Tabs
    tab_habits, tab_lifestyle, tab_unscheduled = st.tabs([
        f"Scheduled Habits ({len(scheduled_habits)})",
        "Lifestyle & Well-being",
        f"Bonus & Other Habits ({len(other_habits)})"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Scheduled Habits
    # -------------------------------------------------------------------------
    with tab_habits:
        c_title, c_quick_btn = st.columns([3.5, 1.5])
        with c_title:
            st.markdown(
                """
                <div style="margin-top: 0.5rem; margin-bottom: 0.75rem;">
                    <div style="font-size: 1.15rem; font-weight: 700; color: var(--db-text);">
                        Scheduled Habits for this Date
                    </div>
                    <div style="font-size: 0.82rem; color: var(--db-text-muted);">
                        Review your targets, select completion status, and record notes.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c_quick_btn:
            st.markdown("<div style='padding-top: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("Mark All as Completed", key=f"quick_all_{date_str}", type="primary", use_container_width=True):
                for h in scheduled_habits:
                    t_val = float(h.get("target_value", 1.0))
                    log_habit_entry(
                        profile_id=p_id,
                        habit_id=h["id"],
                        entry_date=date_str,
                        status="completed",
                        value_recorded=t_val,
                        target_at_entry=t_val
                    )
                st.success("✓ All scheduled habits marked as completed!")
                st.rerun()

        with st.form(key=f"scheduled_form_{date_str}"):
            habit_inputs = {}

            for h in scheduled_habits:
                h_id = h["id"]
                entry = existing_entries.get(h_id)
                target = float(h.get("target_value", 1.0))
                m_type = h.get("measurement_type", "boolean")
                is_completed = entry and entry.get("status") == "completed"
                card_completed_cls = "db-checkin-habit-completed" if is_completed else ""

                circle_icon = '<span class="db-check-circle">✓</span>' if is_completed else '<span class="db-uncheck-circle"></span>'
                cat_badge = get_category_badge_html(h.get("category", "General"))
                routine_badge = f'<span class="db-routine-pill">{h["routine_name"]}</span>' if h.get("routine_name") else ""
                unit_str = h.get("unit", "")
                target_str = f"Target: {target:g} {unit_str}".strip()

                st.markdown(
                    f"""
                    <div class="db-checkin-habit-card {card_completed_cls}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem;">
                            <div style="display: flex; align-items: center; gap: 0.75rem;">
                                {circle_icon}
                                <span style="font-size: 1.15rem; font-weight: 700; color: var(--db-text);">
                                    {h['name']}
                                </span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                                {cat_badge}
                                {routine_badge}
                                <span class="db-target-pill">{target_str}</span>
                            </div>
                        </div>
                    """,
                    unsafe_allow_html=True
                )

                # Responsive Input Controls
                col_status, col_val, col_reason = st.columns([1.5, 1.3, 2.2])

                valid_statuses = ["completed", "partial", "rest_day", "skipped"]
                default_status = "completed"
                if entry and entry.get("status") in valid_statuses:
                    default_status = entry.get("status")

                with col_status:
                    status_val = st.selectbox(
                        "Status",
                        options=valid_statuses,
                        index=valid_statuses.index(default_status) if default_status in valid_statuses else 0,
                        format_func=lambda s: {
                            "completed": "✓ Completed",
                            "partial": "Partial",
                            "rest_day": "Rest Day",
                            "skipped": "Skipped"
                        }.get(s, s),
                        key=f"status_{h_id}_{date_str}",
                        label_visibility="collapsed"
                    )

                with col_val:
                    initial_val = float(entry.get("value_recorded", target)) if entry else target
                    if m_type == "boolean":
                        num_val = target if status_val == "completed" else 0.0
                        label_text = "Target Achieved" if status_val == "completed" else status_val.capitalize()
                        st.markdown(
                            f"""
                            <div style="padding-top: 8px; font-size: 0.88rem; font-weight: 600; color: var(--db-text-secondary);">
                                {label_text}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        num_val = st.number_input(
                            f"Value ({unit_str})",
                            min_value=0.0,
                            max_value=10000.0,
                            value=float(initial_val),
                            step=1.0 if m_type == "count" else 5.0,
                            key=f"val_{h_id}_{date_str}",
                            label_visibility="collapsed"
                        )

                with col_reason:
                    initial_reason = entry.get("skip_reason") or entry.get("notes") or "" if entry else ""
                    skip_reason = st.text_input(
                        "Notes / Reason",
                        value=initial_reason,
                        placeholder="Add an optional note or win...",
                        key=f"reason_{h_id}_{date_str}",
                        label_visibility="collapsed"
                    )

                st.markdown("</div>", unsafe_allow_html=True)

                habit_inputs[h_id] = {
                    "habit": h,
                    "status": status_val,
                    "value": num_val,
                    "target": target,
                    "reason": skip_reason
                }

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            save_habits_btn = st.form_submit_button("Save Habit Entries", type="primary", use_container_width=True)
            if save_habits_btn:
                saved_count = 0
                for h_id, data in habit_inputs.items():
                    log_habit_entry(
                        profile_id=p_id,
                        habit_id=h_id,
                        entry_date=date_str,
                        status=data["status"],
                        value_recorded=data["value"],
                        target_at_entry=data["target"],
                        skip_reason=data["reason"] if data["status"] in ("skipped", "rest_day") else None,
                        notes=data["reason"] if data["status"] not in ("skipped", "rest_day") else None
                    )
                    saved_count += 1
                st.success(f"✓ Successfully saved {saved_count} habit entries for {date_str}!")
                st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: Lifestyle & Well-being (Clear, Attractive Tiles, Zero Formulas)
    # -------------------------------------------------------------------------
    with tab_lifestyle:
        st.markdown(
            """
            <div style="margin-top: 0.5rem; margin-bottom: 0.75rem;">
                <div style="font-size: 1.15rem; font-weight: 700; color: var(--db-text);">
                    Daily Well-being & Energy Journal
                </div>
                <div style="font-size: 0.82rem; color: var(--db-text-muted);">
                    Record your daily sleep, focus, movement, and mood to track your overall consistency.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form(key=f"lifestyle_form_{date_str}"):
            # Tile 1: Sleep
            st.markdown(
                """
                <div class="db-wellness-tile">
                    <div style="font-size: 1rem; font-weight: 700; color: var(--db-text); margin-bottom: 0.6rem;">
                        Sleep & Nightly Rest
                    </div>
                """,
                unsafe_allow_html=True
            )
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                cur_sleep = float(existing_life.get("sleep_hours") or 7.5)
                sleep_hrs = st.number_input(
                    "Sleep Duration (Hours)",
                    min_value=0.0,
                    max_value=24.0,
                    value=cur_sleep,
                    step=0.5,
                    help="Total hours slept last night."
                )
            with c_s2:
                cur_sq = int(existing_life.get("sleep_quality") or 4)
                sleep_qual = st.select_slider(
                    "Sleep Quality Rating",
                    options=[1, 2, 3, 4, 5],
                    value=cur_sq,
                    format_func=lambda q: f"{q} — {SLEEP_QUALITY_LABELS.get(q, '')}"
                )
            st.markdown("</div>", unsafe_allow_html=True)

            # Tile 2: Focus & Study
            st.markdown(
                """
                <div class="db-wellness-tile">
                    <div style="font-size: 1rem; font-weight: 700; color: var(--db-text); margin-bottom: 0.6rem;">
                        Deep Focus & Learning
                    </div>
                """,
                unsafe_allow_html=True
            )
            c_w1, c_w2 = st.columns(2)
            with c_w1:
                cur_study = int(existing_life.get("study_minutes") or 120)
                study_mins = st.number_input(
                    "Focus Time (Minutes)",
                    min_value=0,
                    max_value=1440,
                    value=cur_study,
                    step=15,
                    help="Time spent in deep study or problem solving."
                )
            with c_w2:
                cur_sess = int(existing_life.get("focus_sessions_count") or max(1, cur_study // 45))
                focus_sessions = st.number_input(
                    "Completed Focus Blocks / Sessions",
                    min_value=0,
                    max_value=50,
                    value=cur_sess,
                    step=1
                )
            st.markdown("</div>", unsafe_allow_html=True)

            # Tile 3: Physical Movement
            st.markdown(
                """
                <div class="db-wellness-tile">
                    <div style="font-size: 1rem; font-weight: 700; color: var(--db-text); margin-bottom: 0.6rem;">
                        Physical Activity & Movement
                    </div>
                """,
                unsafe_allow_html=True
            )
            c_e1, c_e2 = st.columns(2)
            with c_e1:
                cur_ex = int(existing_life.get("exercise_minutes") or 30)
                exercise_mins = st.number_input(
                    "Active Movement (Minutes)",
                    min_value=0,
                    max_value=1440,
                    value=cur_ex,
                    step=5
                )
            with c_e2:
                cur_extype = str(existing_life.get("exercise_type") or "Strength Training")
                exercise_type = st.text_input(
                    "Activity Type",
                    value=cur_extype,
                    placeholder="e.g. Gym, Running, Walk, Yoga"
                )
            st.markdown("</div>", unsafe_allow_html=True)

            # Tile 4: Energy & Mood
            st.markdown(
                """
                <div class="db-wellness-tile">
                    <div style="font-size: 1rem; font-weight: 700; color: var(--db-text); margin-bottom: 0.6rem;">
                        Energy & Mood Balance
                    </div>
                """,
                unsafe_allow_html=True
            )
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                cur_energy = int(existing_life.get("energy_score") or 4)
                energy_score = st.select_slider(
                    "Energy Level",
                    options=[1, 2, 3, 4, 5],
                    value=cur_energy,
                    format_func=lambda e: f"{e} — {ENERGY_LABELS.get(e, '')}"
                )
            with c_m2:
                cur_mood = int(existing_life.get("mood_score") or 4)
                mood_score = st.select_slider(
                    "Mood Rating",
                    options=[1, 2, 3, 4, 5],
                    value=cur_mood,
                    format_func=lambda m: f"{m} — {MOOD_LABELS.get(m, '')}"
                )
            st.markdown("</div>", unsafe_allow_html=True)

            # Tile 5: Daily Reflection
            st.markdown(
                """
                <div class="db-wellness-tile">
                    <div style="font-size: 1rem; font-weight: 700; color: var(--db-text); margin-bottom: 0.6rem;">
                        Daily Reflection & Wins
                    </div>
                """,
                unsafe_allow_html=True
            )
            reflection = st.text_area(
                "Daily Journal Notes (Optional)",
                value=str(existing_life.get("reflection_notes") or ""),
                placeholder="What went well today? What gave you momentum or energy?",
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)

            save_life_btn = st.form_submit_button("Save Lifestyle Metrics", type="primary", use_container_width=True)
            if save_life_btn:
                is_valid, errors = validate_lifestyle_inputs(
                    sleep_hours=sleep_hrs,
                    sleep_quality=sleep_qual,
                    study_minutes=study_mins,
                    exercise_minutes=exercise_mins,
                    mood_score=mood_score,
                    energy_score=energy_score
                )
                if not is_valid:
                    for err in errors:
                        st.error(err)
                else:
                    log_lifestyle(
                        profile_id=p_id,
                        log_date=date_str,
                        sleep_hours=sleep_hrs,
                        sleep_quality=sleep_qual,
                        study_minutes=study_mins,
                        focus_sessions_count=focus_sessions,
                        exercise_minutes=exercise_mins,
                        exercise_type=exercise_type,
                        mood_score=mood_score,
                        energy_score=energy_score,
                        reflection_notes=reflection
                    )
                    st.success(f"✓ Lifestyle metrics successfully recorded for {date_str}!")
                    st.rerun()

    # -------------------------------------------------------------------------
    # TAB 3: Bonus / Unscheduled Habits
    # -------------------------------------------------------------------------
    with tab_unscheduled:
        st.markdown(
            """
            <div style="margin-top: 0.5rem; margin-bottom: 0.75rem;">
                <div style="font-size: 1.15rem; font-weight: 700; color: var(--db-text);">
                    Bonus & Off-Schedule Habits
                </div>
                <div style="font-size: 0.82rem; color: var(--db-text-muted);">
                    These habits are not scheduled today (e.g. weekday habits on a weekend). You can still log bonus completions.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not other_habits:
            st.info("All of your active habits are scheduled for this date.")
        else:
            with st.form(key=f"unscheduled_form_{date_str}"):
                unsched_inputs = {}
                for h in other_habits:
                    h_id = h["id"]
                    entry = existing_entries.get(h_id)
                    target = float(h.get("target_value", 1.0))
                    is_completed = entry and entry.get("status") == "completed"

                    circle_icon = '<span class="db-check-circle">✓</span>' if is_completed else '<span class="db-uncheck-circle"></span>'
                    cat_badge = get_category_badge_html(h.get("category", "General"))

                    st.markdown(
                        f"""
                        <div class="db-checkin-habit-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem;">
                                <div style="display: flex; align-items: center; gap: 0.75rem;">
                                    {circle_icon}
                                    <span style="font-size: 1.1rem; font-weight: 700; color: var(--db-text);">
                                        {h['name']}
                                    </span>
                                </div>
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    {cat_badge}
                                    <span class="db-target-pill">{h.get('frequency', '').replace('_', ' ').title()}</span>
                                </div>
                            </div>
                        """,
                        unsafe_allow_html=True
                    )

                    col1, col2 = st.columns([3.0, 1.5])
                    with col1:
                        valid_stat = ["completed", "rest_day", "skipped"]
                        cur_status = entry.get("status", "completed") if entry else "completed"
                        s_idx = valid_stat.index(cur_status) if cur_status in valid_stat else 0
                        st_val = st.selectbox(
                            "Status",
                            options=valid_stat,
                            index=s_idx,
                            format_func=lambda s: {"completed": "✓ Completed (Bonus)", "rest_day": "Rest Day", "skipped": "Skipped"}.get(s, s),
                            key=f"unsched_status_{h_id}",
                            label_visibility="collapsed"
                        )
                    with col2:
                        log_box = st.checkbox("Log This Entry", value=bool(entry), key=f"unsched_chk_{h_id}")

                    st.markdown("</div>", unsafe_allow_html=True)
                    unsched_inputs[h_id] = {"habit": h, "status": st_val, "log": log_box, "target": target}

                save_unsched_btn = st.form_submit_button("Save Bonus Entries", type="primary", use_container_width=True)
                if save_unsched_btn:
                    count = 0
                    for h_id, item in unsched_inputs.items():
                        if item["log"]:
                            log_habit_entry(
                                profile_id=p_id,
                                habit_id=h_id,
                                entry_date=date_str,
                                status=item["status"],
                                value_recorded=item["target"] if item["status"] == "completed" else 0.0,
                                target_at_entry=item["target"]
                            )
                            count += 1
                    st.success(f"✓ Saved {count} bonus habit entries.")
                    st.rerun()


show_daily_checkin()
