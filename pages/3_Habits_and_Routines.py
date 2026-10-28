"""
DayBalance — Section 3: Habits & Routines Management
Redesigned with prominent Bento overview cards, full-width interactive habit cards (NO EXPANDERS),
direct action buttons (Edit, Archive, Delete), routine stacking cards, and clean typography.
"""

from datetime import date, datetime, timedelta
import streamlit as st
from components.theme import apply_custom_css
from components.metric_cards import get_category_badge_html, render_bento_stat_card
from components.modals import render_top_navbar
from config import FREQUENCIES, HABIT_CATEGORIES, MEASUREMENT_TYPES, WEEKDAY_NAMES
from database.repository import (
    archive_habit, create_habit, create_routine,
    delete_habit, delete_routine, get_habit_entries,
    get_habits, get_routines, update_habit, update_routine
)
from services.streaks_service import calculate_profile_streak_summary


def show_habits_and_routines() -> None:
    apply_custom_css()
    profile = render_top_navbar(render_banner=False)
    p_id = profile["id"]
    today = date.today()

    # Fetch habits and data
    habits = get_habits(p_id, include_archived=False)
    archived_habits = [h for h in get_habits(p_id, include_archived=True) if not h.get("is_active", 1)]
    routines = get_routines(p_id)
    routine_map = {r["id"]: r["name"] for r in routines}

    # Fetch streaks for active habits
    ninety_days_ago = (today - timedelta(days=90)).isoformat()
    entries = get_habit_entries(p_id, start_date=ninety_days_ago)
    streak_summary = calculate_profile_streak_summary(habits, entries, today)
    habit_streaks = {
        hm["habit_id"]: hm.get("current_streak", 0)
        for hm in streak_summary.get("habit_metrics", [])
    }

    max_streak = streak_summary.get("max_current_streak", 0)
    lead_habit = next((h["name"] for h in habits if habit_streaks.get(h["id"], 0) == max_streak), "None") if habits else "None"

    # 1. Header (Consistent with Dashboard & Daily Check-in)
    c_hdr_left, c_hdr_right = st.columns([3.2, 1.8])

    with c_hdr_left:
        st.markdown(
            f"""
            <div style="margin-bottom: 0.75rem;">
                <h1 style="font-size: 2.1rem; font-weight: 800; color: var(--db-text); margin: 0; line-height: 1.15; letter-spacing: -0.025em;">
                    Habit & Routine Management
                </h1>
                <div style="font-size: 0.92rem; color: var(--db-text-secondary); margin-top: 0.35rem;">
                    Active Profile: <strong>{profile['name']} (Demo – Student & Builder)</strong> • Design your daily habits and routines
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c_hdr_right:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        c_stat_pill, c_new_btn = st.columns([1.2, 1.8])
        with c_stat_pill:
            st.markdown(
                f"""
                <div style="text-align: right; padding-top: 6px;">
                    <span style="display: inline-block; background: #DEF7EC; color: #047857; font-size: 0.82rem; font-weight: 700; padding: 5px 14px; border-radius: 9999px;">
                        {len(habits)} Active Habits
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c_new_btn:
            if st.button("+ Create New Habit", type="primary", use_container_width=True):
                st.session_state["habit_tab_selected"] = 2
                st.rerun()

    # 2. Bento Stats Overview (4 Clean Cards Across Viewport)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_bento_stat_card(
            label="ACTIVE HABITS",
            value=f"{len(habits)} Habits",
            subtext="Configured in daily schedule",
            icon=None
        )
    with col2:
        render_bento_stat_card(
            label="LONGEST ACTIVE STREAK",
            value=f"{max_streak} Days 🔥",
            subtext=f"Lead habit: {lead_habit}",
            icon="🔥",
            icon_bg="#FEF3C7",
            icon_color="#D97706"
        )
    with col3:
        render_bento_stat_card(
            label="DAILY ROUTINES",
            value=f"{len(routines)} Routines",
            subtext="Grouped habit sequences",
            icon=None
        )
    with col4:
        render_bento_stat_card(
            label="ARCHIVED HABITS",
            value=f"{len(archived_habits)} Archived",
            subtext="Safely preserved history",
            icon=None
        )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. Main Navigation Tabs
    tab_habits, tab_routines, tab_new_habit, tab_archived = st.tabs([
        f"Active Habits ({len(habits)})",
        f"Routines & Stacking ({len(routines)})",
        "+ Create New Habit",
        f"Archived Habits ({len(archived_habits)})"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Active Habits (Full Cards with Direct Buttons, NO EXPANDERS)
    # -------------------------------------------------------------------------
    with tab_habits:
        st.markdown(
            """
            <div style="margin-top: 0.5rem; margin-bottom: 0.85rem;">
                <div style="font-size: 1.15rem; font-weight: 700; color: var(--db-text);">
                    Active Tracked Habits
                </div>
                <div style="font-size: 0.82rem; color: var(--db-text-muted);">
                    Manage your target parameters, assigned routines, and schedule frequency.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not habits:
            st.info("No active habits found. Use the '+ Create New Habit' tab to add your first habit.")
        else:
            for h in habits:
                h_id = h["id"]
                h_streak = habit_streaks.get(h_id, 0)
                cat_badge = get_category_badge_html(h.get("category", "General"))
                r_name = routine_map.get(h.get("routine_id"), "Independent")
                routine_badge = f'<span class="db-routine-pill">{r_name}</span>'
                freq_label = FREQUENCIES.get(h.get("frequency", "daily"), h.get("frequency", "Daily"))
                target_str = f"Target: {h['target_value']:g} {h.get('unit', '')}".strip()
                desc_str = h.get("description") or "Focus on daily consistency and steady progress."

                # State check: is this habit currently in inline-edit mode?
                edit_key = f"is_editing_habit_{h_id}"
                is_editing = st.session_state.get(edit_key, False)

                # Card Header & Badges
                st.markdown(
                    f"""
                    <div class="db-checkin-habit-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                            <div>
                                <div style="display: flex; align-items: center; gap: 0.75rem;">
                                    <span style="font-size: 1.2rem; font-weight: 700; color: var(--db-text);">
                                        {h['name']}
                                    </span>
                                    <span class="db-streak-badge">🔥 {h_streak}d</span>
                                </div>
                                <div style="font-size: 0.85rem; color: var(--db-text-secondary); margin-top: 0.25rem;">
                                    {desc_str}
                                </div>
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                                {cat_badge}
                                {routine_badge}
                                <span class="db-target-pill">{target_str}</span>
                                <span class="db-target-pill">{freq_label}</span>
                            </div>
                        </div>
                    """,
                    unsafe_allow_html=True
                )

                # If NOT editing, show direct action buttons row
                if not is_editing:
                    c_btn_edit, c_btn_arch, c_btn_del, _ = st.columns([1.2, 1.3, 1.2, 3.5])
                    with c_btn_edit:
                        if st.button("Edit Habit", key=f"btn_edit_{h_id}", use_container_width=True):
                            st.session_state[edit_key] = True
                            st.rerun()
                    with c_btn_arch:
                        if st.button("Archive Habit", key=f"btn_arch_{h_id}", use_container_width=True):
                            archive_habit(h_id, p_id)
                            st.success(f"Archived '{h['name']}'. Historical data preserved.")
                            st.rerun()
                    with c_btn_del:
                        with st.popover("Delete"):
                            st.error(f"Permanently delete '{h['name']}'?")
                            st.caption("All historical logs for this habit will be deleted.")
                            if st.button("Confirm Delete", key=f"confirm_del_{h_id}", type="primary"):
                                delete_habit(h_id, p_id)
                                st.success("Habit deleted.")
                                st.rerun()
                else:
                    # Inline Edit Form right inside the card
                    st.markdown("<hr style='margin: 0.75rem 0; border-color: var(--db-border-subtle);'/>", unsafe_allow_html=True)
                    st.markdown("##### Edit Habit Details")
                    with st.form(key=f"inline_edit_form_{h_id}"):
                        c1, c2, c3 = st.columns([2.0, 1.2, 1.2])
                        with c1:
                            edit_name = st.text_input("Habit Name", value=h["name"])
                        with c2:
                            edit_target = st.number_input("Target Value", min_value=0.1, value=float(h["target_value"]), step=1.0)
                        with c3:
                            edit_unit = st.text_input("Unit Label", value=h.get("unit", "times"))

                        c4, c5 = st.columns(2)
                        with c4:
                            edit_cat = st.selectbox(
                                "Category",
                                options=HABIT_CATEGORIES,
                                index=HABIT_CATEGORIES.index(h["category"]) if h["category"] in HABIT_CATEGORIES else 0
                            )
                        with c5:
                            routine_options = [None] + [r["id"] for r in routines]
                            r_idx = routine_options.index(h["routine_id"]) if h.get("routine_id") in routine_options else 0
                            edit_r_id = st.selectbox(
                                "Assigned Routine",
                                options=routine_options,
                                format_func=lambda x: "None (Independent)" if x is None else routine_map.get(x, f"Routine #{x}"),
                                index=r_idx
                            )

                        edit_desc = st.text_area("Description / Motivation", value=h.get("description") or "")

                        c_sub1, c_sub2 = st.columns([1.5, 1.5])
                        with c_sub1:
                            submit_edit = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
                        with c_sub2:
                            cancel_edit = st.form_submit_button("Cancel", use_container_width=True)

                        if submit_edit:
                            update_habit(
                                habit_id=h_id,
                                profile_id=p_id,
                                name=edit_name,
                                target_value=edit_target,
                                unit=edit_unit,
                                category=edit_cat,
                                routine_id=edit_r_id,
                                description=edit_desc
                            )
                            st.session_state[edit_key] = False
                            st.success("✓ Habit updated successfully!")
                            st.rerun()
                        elif cancel_edit:
                            st.session_state[edit_key] = False
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 2: Routines & Stacking (Cards with Direct Buttons, NO EXPANDERS)
    # -------------------------------------------------------------------------
    with tab_routines:
        c_rout_hdr, c_new_rout_btn = st.columns([3.5, 1.5])
        with c_rout_hdr:
            st.markdown(
                """
                <div style="margin-top: 0.5rem; margin-bottom: 0.85rem;">
                    <div style="font-size: 1.15rem; font-weight: 700; color: var(--db-text);">
                        Daily Habit Stacks & Routines
                    </div>
                    <div style="font-size: 0.82rem; color: var(--db-text-muted);">
                        Group sequential habits together into dependable morning and evening routines.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        if not routines:
            st.info("No routines configured yet. Use the '+ Create Routine' section below to build your first stack.")
        else:
            for r in routines:
                r_id = r["id"]
                assigned = [h for h in habits if h.get("routine_id") == r_id]
                time_badge = f'<span class="db-routine-pill">{r["time_of_day"].capitalize()}</span>'

                st.markdown(
                    f"""
                    <div class="db-wellness-tile" style="margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                            <div style="font-size: 1.2rem; font-weight: 700; color: var(--db-text);">
                                {r['name']}
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                {time_badge}
                                <span class="db-target-pill">{len(assigned)} Habits Attached</span>
                            </div>
                        </div>
                        <div style="font-size: 0.9rem; color: var(--db-text-secondary); margin-bottom: 0.75rem;">
                            {r.get('description') or 'Sequential stacked routine.'}
                        </div>
                    """,
                    unsafe_allow_html=True
                )

                if assigned:
                    st.markdown("<div style='font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: var(--db-text-muted); margin-bottom: 0.4rem;'>Stacked Habits in this Routine:</div>", unsafe_allow_html=True)
                    for ah in assigned:
                        ah_cat = get_category_badge_html(ah.get("category", "General"))
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.45rem 0.8rem; background: var(--db-secondary); border-radius: 8px; margin-bottom: 0.35rem; border: 1px solid var(--db-border-subtle);">
                                <span style="font-weight: 600; font-size: 0.92rem; color: var(--db-text);">{ah['name']}</span>
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    {ah_cat}
                                    <span style="font-size: 0.8rem; color: var(--db-text-muted);">Target: {ah['target_value']:g} {ah['unit']}</span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.caption("No habits currently assigned to this routine.")

                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                c_del_r, _ = st.columns([1.5, 4.5])
                with c_del_r:
                    if st.button("Delete Routine", key=f"del_rout_{r_id}", use_container_width=True):
                        delete_routine(r_id, p_id)
                        st.success(f"Routine '{r['name']}' deleted safely (habits unlinked).")
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 1.5rem 0; border-color: var(--db-border-subtle);'/>", unsafe_allow_html=True)
        st.markdown("##### + Add a New Routine")
        with st.form(key="create_routine_form"):
            c_r1, c_r2 = st.columns([2, 1])
            with c_r1:
                r_name = st.text_input("Routine Name *", placeholder="e.g. Morning Launchpad, Evening Wind-Down")
            with c_r2:
                r_time = st.selectbox("Time of Day", options=["morning", "evening", "anytime"], format_func=lambda s: s.capitalize())

            r_desc = st.text_area("Stack Sequence / Motivation", placeholder="e.g. Hydrate -> 20m Walk -> Deep Study")
            submit_rout = st.form_submit_button("Create Routine", type="primary")
            if submit_rout:
                if not r_name.strip():
                    st.error("Routine name is required.")
                else:
                    create_routine(p_id, r_name, r_time, r_desc)
                    st.success(f"✓ Routine '{r_name}' successfully created!")
                    st.rerun()

    # -------------------------------------------------------------------------
    # TAB 3: Create New Habit Form
    # -------------------------------------------------------------------------
    with tab_new_habit:
        st.markdown(
            """
            <div style="margin-top: 0.5rem; margin-bottom: 0.85rem;">
                <div style="font-size: 1.15rem; font-weight: 700; color: var(--db-text);">
                    Create a New Habit
                </div>
                <div style="font-size: 0.82rem; color: var(--db-text-muted);">
                    Set clear target values and scheduling rules for your everyday tracking.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form(key="create_habit_form"):
            c_name, c_cat = st.columns([2, 1])
            with c_name:
                h_name = st.text_input("Habit Name *", placeholder="e.g. Read 20 Pages, Morning Exercise, Deep Study")
            with c_cat:
                h_cat = st.selectbox("Category *", options=HABIT_CATEGORIES, index=1)

            h_desc = st.text_area("Description / Motivation (Optional)", placeholder="Why does this habit matter to you?")

            c_mtype, c_target, c_unit = st.columns(3)
            with c_mtype:
                h_mtype = st.selectbox(
                    "Measurement Type",
                    options=list(MEASUREMENT_TYPES.keys()),
                    format_func=lambda k: MEASUREMENT_TYPES[k]
                )
            with c_target:
                h_target = st.number_input("Target Value", min_value=0.1, max_value=10000.0, value=1.0, step=1.0)
            with c_unit:
                default_unit = "mins" if h_mtype == "duration_minutes" else ("times" if h_mtype == "boolean" else "reps")
                h_unit = st.text_input("Unit Label", value=default_unit)

            c_freq, c_start = st.columns(2)
            with c_freq:
                h_freq = st.selectbox(
                    "Frequency Schedule",
                    options=list(FREQUENCIES.keys()),
                    format_func=lambda k: FREQUENCIES[k]
                )
            with c_start:
                h_start = st.date_input("Start Date", value=date.today())

            custom_days_list = [0, 1, 2, 3, 4, 5, 6]
            if h_freq == "custom_days":
                selected_weekdays = st.multiselect(
                    "Select Active Weekdays",
                    options=list(range(7)),
                    format_func=lambda i: WEEKDAY_NAMES[i],
                    default=[0, 1, 2, 3, 4]
                )
                custom_days_list = selected_weekdays if selected_weekdays else [0, 1, 2, 3, 4]

            routine_opts = [None] + [r["id"] for r in routines]
            h_rout = st.selectbox(
                "Assign to Routine (Optional)",
                options=routine_opts,
                format_func=lambda x: "None (Independent)" if x is None else routine_map.get(x, f"Routine #{x}")
            )

            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            submit_h = st.form_submit_button("Save & Activate Habit", type="primary", use_container_width=True)
            if submit_h:
                if not h_name.strip():
                    st.error("Habit name is required.")
                else:
                    new_h_id = create_habit(
                        profile_id=p_id,
                        name=h_name,
                        category=h_cat,
                        description=h_desc,
                        measurement_type=h_mtype,
                        target_value=h_target,
                        unit=h_unit,
                        frequency=h_freq,
                        custom_days=custom_days_list if h_freq == "custom_days" else None,
                        routine_id=h_rout,
                        start_date=h_start.isoformat()
                    )
                    st.success(f"✓ Habit '{h_name}' created successfully!")
                    st.rerun()

    # -------------------------------------------------------------------------
    # TAB 4: Archived Habits (Full Cards with Restore Button, NO EXPANDERS)
    # -------------------------------------------------------------------------
    with tab_archived:
        st.markdown(
            """
            <div style="margin-top: 0.5rem; margin-bottom: 0.85rem;">
                <div style="font-size: 1.15rem; font-weight: 700; color: var(--db-text);">
                    Archived Habits
                </div>
                <div style="font-size: 0.82rem; color: var(--db-text-muted);">
                    Archived habits are paused from daily check-ins but preserve all historical entries for analytics.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if not archived_habits:
            st.info("No archived habits found. You can archive habits when pausing long-term goals.")
        else:
            for ah in archived_habits:
                ah_cat = get_category_badge_html(ah.get("category", "General"))
                st.markdown(
                    f"""
                    <div class="db-checkin-habit-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                            <div>
                                <span style="font-size: 1.15rem; font-weight: 700; color: var(--db-text);">
                                    {ah['name']}
                                </span>
                                <div style="font-size: 0.82rem; color: var(--db-text-muted); margin-top: 0.2rem;">
                                    Archived: {ah.get('archived_at', 'Previously')}
                                </div>
                            </div>
                            <div>
                                {ah_cat}
                            </div>
                        </div>
                    """,
                    unsafe_allow_html=True
                )

                c_res, _ = st.columns([1.5, 4.5])
                with c_res:
                    if st.button("Restore to Active", key=f"restore_{ah['id']}", type="primary", use_container_width=True):
                        update_habit(ah["id"], p_id, is_active=1, archived_at=None)
                        st.success(f"Restored '{ah['name']}' to active habits.")
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)


show_habits_and_routines()
