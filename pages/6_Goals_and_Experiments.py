"""
DayBalance — Section 6: Goals & Habit Experiments
Structured goal setting, visual milestone progress, and lifestyle experiment evaluation.
"""

from datetime import date, timedelta
import streamlit as st
from components.theme import apply_custom_css
from components.metric_cards import render_header
from components.modals import render_top_navbar
from database.repository import (
    create_experiment, create_goal, delete_experiment,
    delete_goal, get_experiments, get_goals, get_habit_entries,
    get_habits, get_lifestyle_logs, update_experiment, update_goal
)
from services.analytics_service import build_daily_analytics_dataframe
from services.experiments_service import evaluate_experiment
from services.streaks_service import calculate_habit_streak, calculate_profile_streak_summary


def show_goals_and_experiments() -> None:
    apply_custom_css()
    profile = render_top_navbar()
    p_id = profile["id"]
    today = date.today()

    render_header(
        title="Goals & Lifestyle Hypotheses",
        subtitle=f"Set performance milestones and test behavioral lifestyle hypotheses for {profile['name']}."
    )

    # 1. Fetch data
    habits = get_habits(p_id, include_archived=False)
    habit_names = {h["id"]: h["name"] for h in habits}

    ninety_days_ago = (today - timedelta(days=90)).isoformat()
    entries = get_habit_entries(p_id, start_date=ninety_days_ago)
    lifestyle_logs = get_lifestyle_logs(p_id, start_date=ninety_days_ago)
    df = build_daily_analytics_dataframe(habits, entries, lifestyle_logs, start_date=ninety_days_ago)

    all_goals = get_goals(p_id, include_inactive=True)
    active_goals = [g for g in all_goals if g.get("is_active", 1) == 1 and g.get("is_achieved", 0) == 0]
    achieved_goals = [g for g in all_goals if g.get("is_achieved", 0) == 1]

    experiments = get_experiments(p_id)
    active_experiments = [e for e in experiments if e.get("status") == "active"]

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
<span class="db-bento-label">ACTIVE GOALS</span>
<span class="db-stat-badge">In Progress</span>
</div>
<div class="db-bento-value">{len(active_goals)} Goals</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
<div style="background: var(--db-accent); width: {min(100, len(active_goals) * 33)}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub" style="margin-top: 6px;">Active milestone targets</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
    with c_b2:
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">ACHIEVED GOALS</span>
<span class="db-stat-badge">Completed</span>
</div>
<div class="db-bento-value">{len(achieved_goals)} Milestones</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
<div style="background: #059669; width: {min(100, len(achieved_goals) * 50)}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub" style="margin-top: 6px;">Successfully accomplished</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
    with c_b3:
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">HABIT EXPERIMENTS</span>
<span class="db-stat-badge">A/B Testing</span>
</div>
<div class="db-bento-value">{len(active_experiments)} Testing</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
<div style="background: #0284C7; width: {min(100, len(active_experiments) * 50)}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub" style="margin-top: 6px;">Lifestyle tests in progress</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
    with c_b4:
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">LONGEST ACTIVE STREAK</span>
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

    # 3. Tab Navigation
    tab_goals, tab_new_goal, tab_experiments, tab_new_experiment = st.tabs([
        "Active Goals",
        "+ Set New Goal",
        "Habit Experiments (A/B)",
        "+ Launch New Experiment"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Active Goals
    # -------------------------------------------------------------------------
    with tab_goals:
        st.markdown("#### Tracked Goals & Milestones")
        st.caption("Review your progress toward consistency, streak, and focus targets.")

        if not active_goals:
            st.info("No active goals currently set. Use the '+ Set New Goal' tab to define one.")
        else:
            for g in active_goals:
                h_name = habit_names.get(g.get("habit_id"), "All Habits")
                target_val = float(g["target_value"])
                metric = g["target_metric"]

                # Calculate progress from actual data
                progress_pct = 0.0
                current_display = ""
                target_display = ""

                if metric == "completion_rate":
                    g_start = g["start_date"]
                    period_df = df[df["date"] >= g_start] if not df.empty else df
                    avg_c = period_df["completion_rate"].dropna().mean() if not period_df.empty else 0.0
                    progress_pct = min(100.0, (avg_c / target_val) * 100.0) if target_val > 0 else 0.0
                    current_display = f"{avg_c:.1f}% Avg"
                    target_display = f"{target_val:.1f}% Target"
                elif metric == "streak_days":
                    if g.get("habit_id"):
                        h_obj = next((h for h in habits if h["id"] == g["habit_id"]), None)
                        if h_obj:
                            h_entries = {e["entry_date"]: e for e in entries if e["habit_id"] == h_obj["id"]}
                            streak_info = calculate_habit_streak(h_obj, h_entries, today)
                            c_streak = streak_info["current_streak"]
                            progress_pct = min(100.0, (c_streak / target_val) * 100.0)
                            current_display = f"{c_streak} Days"
                            target_display = f"{target_val:.0f} Days"
                    else:
                        c_streak = max_streak
                        progress_pct = min(100.0, (c_streak / target_val) * 100.0)
                        current_display = f"{c_streak} Days"
                        target_display = f"{target_val:.0f} Days"
                elif metric == "total_minutes":
                    g_start = g["start_date"]
                    period_df = df[df["date"] >= g_start] if not df.empty else df
                    tot_mins = period_df["study_minutes"].dropna().sum() if not period_df.empty and "study_minutes" in period_df.columns else 0.0
                    progress_pct = min(100.0, (tot_mins / target_val) * 100.0) if target_val > 0 else 0.0
                    current_display = f"{int(tot_mins)} Mins"
                    target_display = f"{int(target_val)} Mins"
                else:
                    current_display = f"{target_val:g}"
                    target_display = f"{target_val:g}"
                    progress_pct = 50.0

                pct_int = int(round(progress_pct))
                bar_color = "var(--db-accent)" if pct_int < 100 else "#059669"
                end_str = g.get("end_date") or "Ongoing"
                achieved_badge_html = f'<div style="margin-top: 0.75rem; padding: 0.5rem 0.8rem; background: var(--db-accent-light); border-radius: 6px; font-size: 0.85rem; color: var(--db-accent); font-weight: 600;">Target achieved! Consistent performance recorded.</div>' if pct_int >= 100 else ''

                st.markdown(
                    f"""<div class="db-card" style="margin-bottom: 0.75rem; padding: 1.25rem 1.45rem;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem;">
<div>
<div style="display: flex; align-items: center; gap: 0.45rem; margin-bottom: 0.35rem;">
<span class="db-cat-tag db-cat-study">{g['period_type'].capitalize()} Goal</span>
<span class="db-cat-tag db-cat-custom">{h_name}</span>
</div>
<div style="font-size: 1.28rem; font-weight: 700; color: var(--db-text); letter-spacing: -0.015em;">
{g['title']}
</div>
</div>
<div style="text-align: right;">
<span class="db-stat-badge" style="font-size: 0.88rem; padding: 0.25rem 0.65rem; font-weight: 700;">
{pct_int}% Complete
</span>
<div style="font-size: 0.78rem; color: var(--db-text-muted); margin-top: 0.3rem;">
Target End: {end_str}
</div>
</div>
</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 10px; width: 100%; margin: 0.85rem 0 0.6rem 0; overflow: hidden;">
<div style="background: {bar_color}; width: {min(100, pct_int)}%; height: 100%; border-radius: 999px;"></div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.88rem; color: var(--db-text-secondary); margin-top: 0.4rem;">
<span><strong>Current:</strong> {current_display}</span>
<span><strong>Target:</strong> {target_display}</span>
<span><strong>Timeline:</strong> {g['start_date']} &rarr; {end_str}</span>
</div>
{achieved_badge_html}
</div>""",
                    unsafe_allow_html=True
                )

                c_a1, c_a2 = st.columns([1.5, 1.2])
                with c_a1:
                    if st.button("Mark Achieved / Archive", key=f"achieve_goal_{g['id']}", type="primary", use_container_width=True):
                        update_goal(g["id"], p_id, is_achieved=1, is_active=0)
                        st.success("Goal archived as achieved!")
                        st.rerun()
                with c_a2:
                    if st.button("Delete Goal", key=f"del_goal_{g['id']}", use_container_width=True):
                        delete_goal(g["id"], p_id)
                        st.success("Goal deleted.")
                        st.rerun()

                st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 2: Set New Goal
    # -------------------------------------------------------------------------
    with tab_new_goal:
        st.markdown("#### Define a Milestone Goal")
        st.caption("Anchor goals to your genuine baseline rather than arbitrary targets.")

        # Quick Preset Buttons
        st.markdown("<div style='font-size: 0.85rem; font-weight: 600; color: var(--db-text-secondary); margin-bottom: 0.5rem;'>Quick Suggestion Presets:</div>", unsafe_allow_html=True)
        if "goal_preset" not in st.session_state:
            st.session_state["goal_preset"] = {}

        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            if st.button("80% Study Consistency", key="preset_study", use_container_width=True):
                st.session_state["goal_preset"] = {
                    "title": "80% Study Consistency (Monthly)",
                    "metric": "completion_rate",
                    "val": 80.0,
                    "period": "monthly"
                }
                st.rerun()
        with c_p2:
            if st.button("14-Day Streak Challenge", key="preset_streak", use_container_width=True):
                st.session_state["goal_preset"] = {
                    "title": "14-Day Habit Streak Challenge",
                    "metric": "streak_days",
                    "val": 14.0,
                    "period": "challenge"
                }
                st.rerun()
        with c_p3:
            if st.button("120 Mins Daily Deep Work", key="preset_focus", use_container_width=True):
                st.session_state["goal_preset"] = {
                    "title": "120 Mins Daily Deep Work",
                    "metric": "total_minutes",
                    "val": 120.0,
                    "period": "weekly"
                }
                st.rerun()

        st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)

        preset = st.session_state.get("goal_preset", {})
        default_title = preset.get("title", "")
        default_metric = preset.get("metric", "completion_rate")
        default_val = preset.get("val", 80.0)
        default_period = preset.get("period", "weekly")

        with st.form(key="create_goal_form"):
            g_title = st.text_input(
                "Goal Title *",
                value=default_title,
                placeholder="e.g. 85% Study Consistency, 14-Day Meditation Chain"
            )

            c_g1, c_g2 = st.columns(2)
            with c_g1:
                g_habit = st.selectbox(
                    "Assign to Habit",
                    options=[None] + [h["id"] for h in habits],
                    format_func=lambda x: "Overall Profile (All Habits)" if x is None else habit_names.get(x, f"Habit #{x}")
                )
            with c_g2:
                metric_options = ["completion_rate", "streak_days", "total_minutes"]
                metric_idx = metric_options.index(default_metric) if default_metric in metric_options else 0
                g_metric = st.selectbox(
                    "Target Metric",
                    options=metric_options,
                    index=metric_idx,
                    format_func=lambda m: {
                        "completion_rate": "Completion Rate (%)",
                        "streak_days": "Consecutive Streak (Days)",
                        "total_minutes": "Total Time (Minutes)"
                    }.get(m, m)
                )

            c_g3, c_g4 = st.columns(2)
            with c_g3:
                g_target_val = st.number_input(
                    "Target Value *",
                    min_value=1.0,
                    max_value=10000.0,
                    value=float(default_val),
                    step=5.0
                )
            with c_g4:
                period_options = ["weekly", "monthly", "challenge"]
                period_idx = period_options.index(default_period) if default_period in period_options else 0
                g_period = st.selectbox(
                    "Period Type",
                    options=period_options,
                    index=period_idx,
                    format_func=lambda p: p.capitalize()
                )

            c_g5, c_g6 = st.columns(2)
            with c_g5:
                g_start = st.date_input("Start Date", value=today)
            with c_g6:
                g_end = st.date_input("Target End Date (Optional)", value=today + timedelta(days=21))

            submit_g = st.form_submit_button("Create Milestone Goal", type="primary", use_container_width=True)
            if submit_g:
                if not g_title.strip():
                    st.error("Goal title is required.")
                else:
                    create_goal(
                        profile_id=p_id,
                        title=g_title,
                        target_metric=g_metric,
                        target_value=g_target_val,
                        period_type=g_period,
                        start_date=g_start.isoformat(),
                        end_date=g_end.isoformat(),
                        habit_id=g_habit
                    )
                    st.session_state["goal_preset"] = {}
                    st.success(f"Goal '{g_title}' successfully created!")
                    st.rerun()

    # -------------------------------------------------------------------------
    # TAB 3: Habit Experiments (A/B)
    # -------------------------------------------------------------------------
    with tab_experiments:
        st.markdown("#### Lifestyle & Habit Experiments (A/B)")
        st.caption("Compare baseline vs intervention periods to observe changes in study time, sleep, or mood.")

        if not experiments:
            st.info("No habit experiments registered. Launch an experiment in the tab to test a hypothesis.")
        else:
            for exp in experiments:
                eval_res = evaluate_experiment(exp, df)
                h_assoc = habit_names.get(exp.get("habit_id"))
                assoc_pill = f'<span class="db-cat-tag db-cat-custom">{h_assoc}</span>' if h_assoc else ""

                st.markdown(
                    f"""<div class="db-card" style="margin-bottom: 0.75rem; padding: 1.35rem 1.5rem;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem;">
<div>
<div style="display: flex; align-items: center; gap: 0.45rem; margin-bottom: 0.35rem;">
<span class="db-cat-tag db-cat-study">{exp['status'].capitalize()} Testing</span>
{assoc_pill}
</div>
<div style="font-size: 1.3rem; font-weight: 700; color: var(--db-text); letter-spacing: -0.015em;">
{exp['title']}
</div>
</div>
<span class="db-stat-badge" style="font-size: 0.85rem; padding: 0.25rem 0.65rem;">
{eval_res['metric_label']}
</span>
</div>
<div style="font-style: italic; font-size: 0.95rem; color: var(--db-text-secondary); padding: 0.65rem 0.95rem; background: var(--db-border-subtle); border-radius: 8px; margin: 0.6rem 0 0.8rem 0; border-left: 3px solid var(--db-accent);">
"{exp['hypothesis']}"
</div>
<div style="font-size: 0.84rem; color: var(--db-text-muted);">
<strong>Baseline:</strong> {exp['baseline_start']} &rarr; {exp['baseline_end']} &nbsp;|&nbsp; <strong>Intervention:</strong> {exp['intervention_start']} &rarr; {exp['intervention_end']}
</div>
</div>""",
                    unsafe_allow_html=True
                )

                if not eval_res["has_data"]:
                    st.warning(eval_res["message"])
                else:
                    b_mean = eval_res["baseline_mean"]
                    i_mean = eval_res["intervention_mean"]
                    diff = eval_res["difference"]
                    pct_change = eval_res["pct_change"]
                    direction = eval_res["direction"]
                    metric_unit = "mins" if "minute" in eval_res["metric_label"].lower() else (
                        "hrs" if "hour" in eval_res["metric_label"].lower() else (
                            "%" if "%" in eval_res["metric_label"] else "/5"
                        )
                    )

                    # 4 Top Visual Metric Bars of the Experiment
                    c1, c2, c3, c4 = st.columns(4)

                    # Bar 1: Baseline Average
                    with c1:
                        st.markdown(
                            f"""<div class="db-card" style="margin-bottom: 0.5rem; padding: 1rem 1.15rem; background: var(--db-surface);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
<span class="db-bento-label">BASELINE AVG</span>
<span class="db-stat-badge" style="background: var(--db-border-subtle); color: var(--db-text-muted);">Before</span>
</div>
<div class="db-bento-value" style="font-size: 1.5rem; margin-bottom: 0.35rem;">{b_mean:.1f} <span style="font-size: 0.85rem; font-weight: 500; color: var(--db-text-muted);">{metric_unit}</span></div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 8px; width: 100%; margin: 8px 0; overflow: hidden;">
<div style="background: #94A3B8; width: 55%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub">{eval_res['baseline_n']} Tracked Days</div>
</div>""",
                            unsafe_allow_html=True
                        )

                    # Bar 2: Intervention Average
                    with c2:
                        st.markdown(
                            f"""<div class="db-card" style="margin-bottom: 0.5rem; padding: 1rem 1.15rem; background: var(--db-surface);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
<span class="db-bento-label">INTERVENTION AVG</span>
<span class="db-stat-badge">During</span>
</div>
<div class="db-bento-value" style="font-size: 1.5rem; margin-bottom: 0.35rem;">{i_mean:.1f} <span style="font-size: 0.85rem; font-weight: 500; color: var(--db-text-muted);">{metric_unit}</span></div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 8px; width: 100%; margin: 8px 0; overflow: hidden;">
<div style="background: var(--db-accent); width: 75%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub">{eval_res['intervention_n']} Tracked Days</div>
</div>""",
                            unsafe_allow_html=True
                        )

                    # Bar 3: Observed Change
                    with c3:
                        pct_display = f"{pct_change:+g}%" if pct_change is not None else ""
                        chg_color = "var(--db-accent)" if diff >= 0 else "var(--db-warning)"
                        st.markdown(
                            f"""<div class="db-card" style="margin-bottom: 0.5rem; padding: 1rem 1.15rem; background: var(--db-surface);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
<span class="db-bento-label">OBSERVED CHANGE</span>
<span class="db-stat-badge" style="color: {chg_color};">{pct_display}</span>
</div>
<div class="db-bento-value" style="font-size: 1.5rem; margin-bottom: 0.35rem; color: {chg_color};">{diff:+g} <span style="font-size: 0.85rem; font-weight: 500; color: var(--db-text-muted);">{metric_unit}</span></div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 8px; width: 100%; margin: 8px 0; overflow: hidden;">
<div style="background: {chg_color}; width: {min(100, max(15, int(abs(pct_change or 15))))}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub">Net change observed</div>
</div>""",
                            unsafe_allow_html=True
                        )

                    # Bar 4: Experiment Outcome
                    with c4:
                        if direction == "increase":
                            out_title = "Positive Shift"
                            out_badge = "Boost"
                            out_dir = "↗ Upward"
                            out_color = "var(--db-accent)"
                            out_sub = "Performance improved"
                        elif direction == "decrease":
                            out_title = "Downshift"
                            out_badge = "Lower"
                            out_dir = "↘ Downward"
                            out_color = "var(--db-warning)"
                            out_sub = "Metric decreased"
                        else:
                            out_title = "Steady"
                            out_badge = "Even"
                            out_dir = "→ Balanced"
                            out_color = "var(--db-text-muted)"
                            out_sub = "No change observed"

                        st.markdown(
                            f"""<div class="db-card" style="margin-bottom: 0.5rem; padding: 1rem 1.15rem; background: var(--db-surface);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
<span class="db-bento-label">EXPERIMENT OUTCOME</span>
<span class="db-stat-badge">{out_badge}</span>
</div>
<div class="db-bento-value" style="font-size: 1.5rem; margin-bottom: 0.35rem;">{out_title}</div>
<div style="display: flex; align-items: center; gap: 8px; margin: 8px 0;">
<div style="flex: 1; height: 8px; background: var(--db-border-subtle); border-radius: 999px; overflow: hidden; position: relative;">
<div style="position: absolute; left: 0; width: 100%; height: 100%; background: linear-gradient(90deg, #10B981, #0284C7); border-radius: 999px;"></div>
</div>
<span style="font-size: 0.78rem; font-weight: 700; color: {out_color}; white-space: nowrap;">{out_dir}</span>
</div>
<div class="db-bento-sub">{out_sub}</div>
</div>""",
                            unsafe_allow_html=True
                        )

                    # Clean Key Finding Card
                    pct_str = f" ({pct_change:+g}%)" if pct_change is not None else ""
                    st.markdown(
                        f"""<div class="db-card" style="border-left: 4px solid var(--db-accent); margin: 0.9rem 0; padding: 1.1rem 1.35rem;">
<div style="font-weight: 700; font-size: 1.05rem; color: var(--db-text); margin-bottom: 0.35rem;">
Key Experiment Finding
</div>
<div style="font-size: 0.94rem; color: var(--db-text-secondary); line-height: 1.55;">
During the intervention period, your <strong>{eval_res['metric_label'].lower()}</strong> averaged <strong>{i_mean:.1f} {metric_unit}</strong>, compared to <strong>{b_mean:.1f} {metric_unit}</strong> during the baseline period. This represents an observed <strong>{abs(diff):.1f} {metric_unit} {direction}{pct_str}</strong>.
</div>
<div style="font-size: 0.85rem; color: var(--db-text-muted); margin-top: 0.65rem; padding-top: 0.5rem; border-top: 1px solid var(--db-border-subtle);">
<strong>Practical Takeaway:</strong> Consistent morning routines show a clear positive impact on your focus. Continue this routine to solidify long-term momentum.
</div>
</div>""",
                        unsafe_allow_html=True
                    )

                c_act1, c_act2 = st.columns(2)
                with c_act1:
                    if exp["status"] == "active":
                        with st.popover("Conclude Experiment", use_container_width=True):
                            conc_notes = st.text_area("Conclusion Notes", value=exp.get("conclusion_notes") or "")
                            if st.button("Conclude & Complete", key=f"conc_{exp['id']}", type="primary", use_container_width=True):
                                update_experiment(exp["id"], p_id, status="completed", conclusion_notes=conc_notes)
                                st.success("Experiment concluded.")
                                st.rerun()
                with c_act2:
                    if st.button("Delete Experiment", key=f"del_exp_{exp['id']}", use_container_width=True):
                        delete_experiment(exp["id"], p_id)
                        st.success("Experiment deleted.")
                        st.rerun()

                st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # TAB 4: Launch New Experiment
    # -------------------------------------------------------------------------
    with tab_new_experiment:
        st.markdown("#### Formulate a Personal Experiment")
        st.caption("Design a structured A/B comparison to test a lifestyle change.")

        with st.form(key="create_experiment_form"):
            e_title = st.text_input(
                "Experiment Title *",
                placeholder="e.g. Morning 15m Meditation vs Afternoon Deep Study"
            )
            e_hypo = st.text_area(
                "Hypothesis *",
                placeholder="e.g. Adding morning meditation will reduce study friction and increase daily study time by 20+ minutes."
            )

            c_m, c_h = st.columns(2)
            with c_m:
                e_metric = st.selectbox(
                    "Primary Target Metric",
                    options=["study_minutes", "sleep_hours", "completion_rate", "mood_score", "energy_score", "exercise_minutes"],
                    format_func=lambda m: {
                        "study_minutes": "Study Time (Minutes)",
                        "sleep_hours": "Sleep Duration (Hours)",
                        "completion_rate": "Habit Completion Rate (%)",
                        "mood_score": "Mood Rating (1-5)",
                        "energy_score": "Energy Rating (1-5)",
                        "exercise_minutes": "Exercise (Minutes)"
                    }.get(m, m)
                )
            with c_h:
                e_habit = st.selectbox(
                    "Associated Habit (Optional)",
                    options=[None] + [h["id"] for h in habits],
                    format_func=lambda x: "None (Lifestyle Factor)" if x is None else habit_names.get(x, f"Habit #{x}")
                )

            st.markdown("<div style='font-size: 0.88rem; font-weight: 600; color: var(--db-text); margin: 0.5rem 0;'>Baseline Period (Historical Comparison):</div>", unsafe_allow_html=True)
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                b_start = st.date_input("Baseline Period Start", value=today - timedelta(days=28))
            with c_b2:
                b_end = st.date_input("Baseline Period End", value=today - timedelta(days=15))

            st.markdown("<div style='font-size: 0.88rem; font-weight: 600; color: var(--db-text); margin: 0.5rem 0;'>Intervention Period (Testing Window):</div>", unsafe_allow_html=True)
            c_i1, c_i2 = st.columns(2)
            with c_i1:
                i_start = st.date_input("Intervention Period Start", value=today - timedelta(days=14))
            with c_i2:
                i_end = st.date_input("Intervention Period End", value=today)

            submit_exp = st.form_submit_button("Launch Habit Experiment", type="primary", use_container_width=True)
            if submit_exp:
                if not e_title.strip() or not e_hypo.strip():
                    st.error("Title and Hypothesis are required.")
                elif b_start >= b_end or i_start >= i_end or b_end >= i_start:
                    st.error("Date ranges must be sequential (Baseline Start < Baseline End < Intervention Start < Intervention End).")
                else:
                    create_experiment(
                        profile_id=p_id,
                        title=e_title,
                        hypothesis=e_hypo,
                        primary_metric=e_metric,
                        baseline_start=b_start.isoformat(),
                        baseline_end=b_end.isoformat(),
                        intervention_start=i_start.isoformat(),
                        intervention_end=i_end.isoformat(),
                        habit_id=e_habit
                    )
                    st.success(f"Experiment '{e_title}' launched successfully!")
                    st.rerun()


show_goals_and_experiments()
