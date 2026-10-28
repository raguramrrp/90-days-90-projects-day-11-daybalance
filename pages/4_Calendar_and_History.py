"""
DayBalance — Section 4: Calendar & History
Interactive date-based tracking log, calendar activity matrix, status legend, and history editor.
"""

from datetime import date, datetime, timedelta
import streamlit as st
import pandas as pd
from components.theme import apply_custom_css, get_current_theme
from components.metric_cards import render_calendar_legend, render_header, render_status_badge
from components.charts import create_calendar_activity_heatmap
from components.modals import render_top_navbar
from database.repository import (
    get_daily_habit_entries_map, get_habit_entries,
    get_habits, get_lifestyle_logs, get_routines, log_habit_entry
)
from services.analytics_service import build_daily_analytics_dataframe
from services.habits_service import resolve_daily_habit_status


def show_calendar_and_history() -> None:
    apply_custom_css()
    profile = render_top_navbar()
    p_id = profile["id"]
    theme_mode = get_current_theme()
    today = date.today()

    render_header(
        title="Calendar Matrix & Consistency History",
        subtitle=f"Audit your historical consistency, inspect past entries, and correct records for {profile['name']}."
    )

    # 1. Filters
    habits = get_habits(p_id, include_archived=True)
    routines = get_routines(p_id)

    f_col1, f_col2, f_col3 = st.columns([1.5, 1.2, 1.3])
    with f_col1:
        date_range_choice = st.selectbox(
            "Historical Date Range",
            options=["Last 14 Days", "Last 30 Days", "Last 60 Days", "Last 90 Days", "Custom Range"],
            index=1
        )
    with f_col2:
        habit_filter = st.selectbox(
            "Filter by Habit",
            options=[None] + [h["id"] for h in habits],
            format_func=lambda x: "All Habits" if x is None else next((h["name"] for h in habits if h["id"] == x), f"#{x}")
        )
    with f_col3:
        status_filter = st.selectbox(
            "Filter by Status",
            options=["All Statuses", "Completed", "Partial", "Rest Day", "Skipped", "Missed"]
        )

    # Calculate date bounds
    if date_range_choice == "Last 14 Days":
        start_d = today - timedelta(days=14)
        end_d = today
    elif date_range_choice == "Last 30 Days":
        start_d = today - timedelta(days=30)
        end_d = today
    elif date_range_choice == "Last 60 Days":
        start_d = today - timedelta(days=60)
        end_d = today
    elif date_range_choice == "Last 90 Days":
        start_d = today - timedelta(days=90)
        end_d = today
    else:
        c_dr1, c_dr2 = st.columns(2)
        with c_dr1:
            start_d = st.date_input("Start Date", value=today - timedelta(days=30))
        with c_dr2:
            end_d = st.date_input("End Date", value=today)

    start_str = start_d.isoformat()
    end_str = end_d.isoformat()

    # Fetch data in range
    entries = get_habit_entries(p_id, start_date=start_str, end_date=end_str, habit_id=habit_filter)
    lifestyle_logs = get_lifestyle_logs(p_id, start_date=start_str, end_date=end_str)

    # Activity Heatmap
    df = build_daily_analytics_dataframe(habits, entries, lifestyle_logs, start_date=start_str, end_date=end_str)
    st.plotly_chart(create_calendar_activity_heatmap(df, theme_mode), use_container_width=True)
    render_calendar_legend()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    tab_table, tab_inspect = st.tabs(["Historical Log Records", "Date Inspector & Quick Correction"])

    # -------------------------------------------------------------------------
    # TAB 1: Historical Log Table
    # -------------------------------------------------------------------------
    with tab_table:
        if not entries:
            st.info("No habit entries recorded in the selected date range.")
        else:
            rows = []
            for e in entries:
                st_label = e.get("status", "completed").capitalize()
                if status_filter != "All Statuses" and st_label.lower() != status_filter.lower():
                    continue

                rows.append({
                    "Date": e["entry_date"],
                    "Habit": e["habit_name"],
                    "Category": e.get("category", ""),
                    "Status": st_label,
                    "Recorded": f"{e['value_recorded']:g} {e.get('unit', '')}",
                    "Target at Entry": f"{e['target_at_entry']:g} {e.get('unit', '')}",
                    "Skip Reason / Notes": e.get("skip_reason") or e.get("notes") or ""
                })

            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                st.caption(f"Showing {len(rows)} matching historical logs.")
            else:
                st.info("No records matched the selected status filter.")

    # -------------------------------------------------------------------------
    # TAB 2: Date Inspector & Quick Correction
    # -------------------------------------------------------------------------
    with tab_inspect:
        st.markdown("#### Inspect & Correct Entries for a Specific Date")
        st.caption("Select any date to review what was logged, adjust values, or update reasons.")

        inspect_date = st.date_input("Date to Inspect", value=today, max_value=today, key="inspect_date_picker")
        inspect_str = inspect_date.isoformat()

        day_entries = get_daily_habit_entries_map(p_id, inspect_str)

        if not habits:
            st.info("No habits to inspect.")
        else:
            for h in habits:
                entry = day_entries.get(h["id"])
                status_info = resolve_daily_habit_status(h, entry, inspect_date, today)

                with st.expander(f"{status_info['symbol']} {h['name']} — {status_info['label']}", expanded=bool(entry)):
                    with st.form(key=f"correct_form_{h['id']}_{inspect_str}"):
                        c1, c2, c3 = st.columns(3)
                        valid_stat_opts = ["completed", "partial", "rest_day", "skipped"]
                        entry_status = entry.get("status", "completed") if entry else "completed"
                        stat_idx = valid_stat_opts.index(entry_status) if entry_status in valid_stat_opts else 0
                        with c1:
                            new_status = st.selectbox(
                                "Status",
                                options=valid_stat_opts,
                                index=stat_idx,
                                key=f"c_st_{h['id']}_{inspect_str}"
                            )
                        with c2:
                            current_val = float(entry.get("value_recorded", h["target_value"])) if entry else float(h["target_value"])
                            new_val = st.number_input(
                                f"Recorded Value ({h.get('unit', '')})",
                                min_value=0.0,
                                value=current_val,
                                step=1.0,
                                key=f"c_val_{h['id']}_{inspect_str}"
                            )
                        with c3:
                            current_notes = entry.get("skip_reason") or entry.get("notes") or "" if entry else ""
                            new_notes = st.text_input("Notes / Skip Reason", value=current_notes, key=f"c_notes_{h['id']}_{inspect_str}")

                        submit_correction = st.form_submit_button("Update Entry", type="primary")
                        if submit_correction:
                            log_habit_entry(
                                profile_id=p_id,
                                habit_id=h["id"],
                                entry_date=inspect_str,
                                status=new_status,
                                value_recorded=new_val,
                                target_at_entry=float(h["target_value"]),
                                skip_reason=new_notes if new_status in ("skipped", "rest_day") else None,
                                notes=new_notes if new_status not in ("skipped", "rest_day") else None
                            )
                            st.success(f"✓ Updated record for '{h['name']}' on {inspect_str}.")
                            st.rerun()


show_calendar_and_history()
