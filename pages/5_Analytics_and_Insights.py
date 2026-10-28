"""
DayBalance — Section 5: Analytics & Behavioral Insights
Intuitive habit connections, visual relationship indicators, weekday consistency rhythm,
and deterministic behavioral insights.
"""

from datetime import date, timedelta
import streamlit as st
import pandas as pd
from components.theme import apply_custom_css, get_current_theme
from components.metric_cards import render_header
from components.charts import (
    create_completion_trend_chart, create_correlation_scatter_chart,
    create_lifestyle_trend_chart, create_weekday_bar_chart
)
from components.modals import render_top_navbar
from config import MIN_CORRELATION_PAIRS
from database.repository import get_habit_entries, get_habits, get_lifestyle_logs, get_routines
from services.analytics_service import (
    build_daily_analytics_dataframe, calculate_relationship,
    compute_rolling_averages, compute_weekday_performance
)
from services.insights_service import generate_behavioral_insights
from services.lifestyle_service import format_duration_hm
from services.streaks_service import calculate_profile_streak_summary


def show_analytics_and_insights() -> None:
    apply_custom_css()
    profile = render_top_navbar()
    p_id = profile["id"]
    theme_mode = get_current_theme()
    today = date.today()

    render_header(
        title="Analytics & Habit Insights",
        subtitle=f"Personal consistency trends, habit connections, and behavioral patterns for {profile['name']}."
    )

    # 1. Fetch data
    habits = get_habits(p_id, include_archived=False)
    ninety_days_ago = (today - timedelta(days=90)).isoformat()
    entries = get_habit_entries(p_id, start_date=ninety_days_ago)
    lifestyle_logs = get_lifestyle_logs(p_id, start_date=ninety_days_ago)
    routines = get_routines(p_id)

    if not habits:
        st.info("No habits recorded yet. Add habits to generate behavioral analytics.")
        return

    df = build_daily_analytics_dataframe(habits, entries, lifestyle_logs, start_date=ninety_days_ago)
    df_rolling = compute_rolling_averages(df, window=7)
    df_weekday = compute_weekday_performance(df)
    streak_summary = calculate_profile_streak_summary(habits, entries, today)

    # 2. Compute Top Bento Metrics
    comp_rate = streak_summary.get("overall_completion_rate", 0.0)
    max_streak = streak_summary.get("max_current_streak", 0)
    best_streak = streak_summary.get("best_overall_streak", 0)

    if not df_weekday.empty and "avg_completion_rate" in df_weekday.columns:
        best_row = df_weekday.loc[df_weekday["avg_completion_rate"].idxmax()]
        best_day_str = f"{best_row['weekday_name']} ({best_row['avg_completion_rate']:.0f}%)"
    else:
        best_day_str = "No Data"

    avg_study_mins = (
        round(df["study_minutes"].dropna().mean())
        if not df.empty and "study_minutes" in df.columns and not df["study_minutes"].dropna().empty
        else 0
    )
    focus_str = format_duration_hm(avg_study_mins) if avg_study_mins > 0 else "0m"

    # 3. Render Top 4 Bento Overview Cards
    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    with c_b1:
        st.markdown(
            f"""
            <div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
                <div class="db-bento-content" style="width: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="db-bento-label">OVERALL CONSISTENCY</span>
                        <span class="db-stat-badge">30 Days</span>
                    </div>
                    <div class="db-bento-value">{comp_rate:.1f}%</div>
                    <div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
                        <div style="background: var(--db-accent); width: {min(100, max(0, int(round(comp_rate))))}%; height: 100%; border-radius: 999px;"></div>
                    </div>
                    <div class="db-bento-sub" style="margin-top: 6px;">Based on scheduled habits</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c_b2:
        st.markdown(
            f"""
            <div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
                <div class="db-bento-content" style="width: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="db-bento-label">PEAK WEEKDAY</span>
                        <span class="db-stat-badge">Top Rhythm</span>
                    </div>
                    <div class="db-bento-value" style="font-size: 1.4rem;">{best_day_str}</div>
                    <div style="height: 6px; width: 100%; margin-top: 6px;"></div>
                    <div class="db-bento-sub" style="margin-top: 6px;">Highest completion rate</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c_b3:
        st.markdown(
            f"""
            <div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
                <div class="db-bento-content" style="width: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="db-bento-label">LONGEST ACTIVE STREAK</span>
                        <span class="db-stat-badge">Record</span>
                    </div>
                    <div class="db-bento-value">{max_streak} Days 🔥</div>
                    <div style="height: 6px; width: 100%; margin-top: 6px;"></div>
                    <div class="db-bento-sub" style="margin-top: 6px;">Best all-time streak: {best_streak} days</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c_b4:
        st.markdown(
            f"""
            <div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
                <div class="db-bento-content" style="width: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="db-bento-label">DAILY FOCUS AVERAGE</span>
                        <span class="db-stat-badge">Deep Work</span>
                    </div>
                    <div class="db-bento-value">{focus_str}</div>
                    <div style="height: 6px; width: 100%; margin-top: 6px;"></div>
                    <div class="db-bento-sub" style="margin-top: 6px;">Average focus per logged day</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    # 4. Tab Navigation
    tab_correlations, tab_insights, tab_weekday, tab_trends = st.tabs([
        "Habit Connections",
        "Behavioral Insights",
        "Weekday Consistency",
        "Rolling Trends"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Habit & Lifestyle Connections
    # -------------------------------------------------------------------------
    with tab_correlations:
        st.markdown("#### Habit & Lifestyle Connections")
        st.caption(
            "See how your habits, sleep, study time, and energy naturally connect with each other. "
            f"Requires at least {MIN_CORRELATION_PAIRS} tracked days to identify reliable patterns."
        )

        selectable_metrics = [
            ("sleep_hours", "Sleep Duration (Hours)"),
            ("study_minutes", "Study / Focus Time (Minutes)"),
            ("exercise_minutes", "Exercise Duration (Minutes)"),
            ("mood_score", "Self-Reported Mood (1-5)"),
            ("energy_score", "Self-Reported Energy (1-5)"),
            ("completion_rate", "Habit Completion Rate (%)")
        ]
        metric_keys = [k for k, _ in selectable_metrics]
        metric_labels = {k: label for k, label in selectable_metrics}

        c_v1, c_v2, c_min = st.columns([1.5, 1.5, 1.0])
        with c_v1:
            x_metric = st.selectbox(
                "First Habit or Metric",
                options=metric_keys,
                index=0,
                format_func=lambda k: metric_labels[k]
            )
        with c_v2:
            y_metric = st.selectbox(
                "Second Habit or Metric",
                options=metric_keys,
                index=1,
                format_func=lambda k: metric_labels[k]
            )
        with c_min:
            custom_min_pairs = st.number_input(
                "Min Tracked Days",
                min_value=5,
                max_value=30,
                value=MIN_CORRELATION_PAIRS,
                step=1
            )

        if x_metric == y_metric:
            st.warning("Please select two distinct habits or metrics to explore how they connect.")
        else:
            rel = calculate_relationship(df, x_metric, y_metric, min_pairs=custom_min_pairs)

            if not rel["is_sufficient"]:
                st.info(f"Need More Data: {rel['message']}")
            else:
                r_val = rel["pearson_r"]
                pct_match = int(round(abs(r_val) * 100))
                direction = rel["direction"]
                strength = rel["strength"]
                n_pairs = rel["n_pairs"]

                # 4 Top Visual Metric Bars
                c1, c2, c3, c4 = st.columns(4)

                # Bar 1: Connection Match
                with c1:
                    match_sub = (
                        "Strong pattern similarity" if pct_match >= 70
                        else ("Noticeable connection" if pct_match >= 40 else "Subtle connection")
                    )
                    st.markdown(
                        f"""
                        <div class="db-card" style="margin-bottom: 0.5rem; padding: 1.1rem 1.25rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                                <span class="db-bento-label">CONNECTION MATCH</span>
                                <span class="db-stat-badge">{strength}</span>
                            </div>
                            <div class="db-bento-value" style="font-size: 1.55rem; margin-bottom: 0.35rem;">{pct_match}% Match</div>
                            <div style="background: var(--db-border-subtle); border-radius: 999px; height: 8px; width: 100%; margin: 8px 0; overflow: hidden;">
                                <div style="background: var(--db-accent); width: {pct_match}%; height: 100%; border-radius: 999px;"></div>
                            </div>
                            <div class="db-bento-sub">{match_sub}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Bar 2: Relationship Direction
                with c2:
                    if direction == "Positive":
                        dir_title = "Moves Together"
                        dir_badge = "Aligned"
                        dir_sub = "Both habits rise and fall together"
                        dir_symbol = "↗ Upward"
                        grad = "linear-gradient(90deg, #10B981, #0284C7)"
                        sym_color = "var(--db-accent)"
                    elif direction == "Negative":
                        dir_title = "Balances Out"
                        dir_badge = "Inverse"
                        dir_sub = "Habits alternate or balance each other"
                        dir_symbol = "↘ Balanced"
                        grad = "linear-gradient(90deg, #F59E0B, #6366F1)"
                        sym_color = "var(--db-warning)"
                    else:
                        dir_title = "Independent"
                        dir_badge = "Neutral"
                        dir_sub = "No strong pattern between habits"
                        dir_symbol = "→ Steady"
                        grad = "linear-gradient(90deg, #94A3B8, #CBD5E1)"
                        sym_color = "var(--db-text-muted)"

                    st.markdown(
                        f"""
                        <div class="db-card" style="margin-bottom: 0.5rem; padding: 1.1rem 1.25rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                                <span class="db-bento-label">RELATIONSHIP TYPE</span>
                                <span class="db-stat-badge">{dir_badge}</span>
                            </div>
                            <div class="db-bento-value" style="font-size: 1.55rem; margin-bottom: 0.35rem;">{dir_title}</div>
                            <div style="display: flex; align-items: center; gap: 8px; margin: 8px 0;">
                                <div style="flex: 1; height: 8px; background: var(--db-border-subtle); border-radius: 999px; overflow: hidden; position: relative;">
                                    <div style="position: absolute; left: 0; width: 100%; height: 100%; background: {grad}; border-radius: 999px;"></div>
                                </div>
                                <span style="font-size: 0.78rem; font-weight: 700; color: {sym_color}; white-space: nowrap;">{dir_symbol}</span>
                            </div>
                            <div class="db-bento-sub">{dir_sub}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Bar 3: Habit Influence / Impact
                with c3:
                    abs_val = abs(r_val)
                    if abs_val >= 0.75:
                        active_segments = 5
                    elif abs_val >= 0.55:
                        active_segments = 4
                    elif abs_val >= 0.35:
                        active_segments = 3
                    elif abs_val >= 0.20:
                        active_segments = 2
                    else:
                        active_segments = 1

                    segments_html = "".join([
                        f'<div style="flex: 1; height: 8px; border-radius: 4px; background: {"var(--db-accent)" if i <= active_segments else "var(--db-border-subtle)"};"></div>'
                        for i in range(1, 6)
                    ])

                    st.markdown(
                        f"""
                        <div class="db-card" style="margin-bottom: 0.5rem; padding: 1.1rem 1.25rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                                <span class="db-bento-label">EVERYDAY IMPACT</span>
                                <span class="db-stat-badge">{active_segments}/5 Meter</span>
                            </div>
                            <div class="db-bento-value" style="font-size: 1.55rem; margin-bottom: 0.35rem;">{strength} Impact</div>
                            <div style="display: flex; gap: 4px; width: 100%; margin: 8px 0;">
                                {segments_html}
                            </div>
                            <div class="db-bento-sub">Noticeable everyday impact</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Bar 4: Data Reliability & Tracked Sample
                with c4:
                    conf_pct = min(100, int((n_pairs / 30) * 100))
                    conf_tag = "High Confidence" if n_pairs >= 25 else ("Good Sample" if n_pairs >= 14 else "Baseline")
                    st.markdown(
                        f"""
                        <div class="db-card" style="margin-bottom: 0.5rem; padding: 1.1rem 1.25rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                                <span class="db-bento-label">DATA RELIABILITY</span>
                                <span class="db-stat-badge">{conf_tag}</span>
                            </div>
                            <div class="db-bento-value" style="font-size: 1.55rem; margin-bottom: 0.35rem;">{n_pairs} Days Tracked</div>
                            <div style="background: var(--db-border-subtle); border-radius: 999px; height: 8px; width: 100%; margin: 8px 0; overflow: hidden;">
                                <div style="background: #0284C7; width: {conf_pct}%; height: 100%; border-radius: 999px;"></div>
                            </div>
                            <div class="db-bento-sub">Exceeds {custom_min_pairs}-day tracking baseline</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Scatter Chart
                st.plotly_chart(create_correlation_scatter_chart(rel, theme_mode), use_container_width=True)

                # Clean Takeaway Card (No complex mathematical jargon or formulas)
                x_label = metric_labels.get(x_metric, x_metric)
                y_label = metric_labels.get(y_metric, y_metric)
                st.markdown(
                    f"""
                    <div class="db-card" style="border-left: 4px solid var(--db-accent); margin-top: 1rem; padding: 1.15rem 1.35rem;">
                        <div style="font-weight: 700; font-size: 1.08rem; margin-bottom: 0.35rem; color: var(--db-text);">
                            Key Habit Takeaway
                        </div>
                        <div style="font-size: 0.95rem; color: var(--db-text-secondary); line-height: 1.55;">
                            A <strong>{strength.lower()} {direction.lower()} relationship</strong> was observed across <strong>{n_pairs} tracked days</strong>.
                            On days when your <em>{x_label.lower()}</em> is higher, your <em>{y_label.lower()}</em> tends to follow in a consistent pattern.
                        </div>
                        <div style="font-size: 0.86rem; color: var(--db-text-muted); margin-top: 0.75rem; padding-top: 0.6rem; border-top: 1px solid var(--db-border-subtle);">
                            <strong>Consistency Tip:</strong> When one habit strengthens, it naturally builds momentum for your other daily routines.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # -------------------------------------------------------------------------
    # TAB 2: Personal Behavioral Insights
    # -------------------------------------------------------------------------
    with tab_insights:
        st.markdown("#### Personal Behavioral Insights")
        st.caption("Observed patterns and consistency triggers based on your actual tracking history.")

        insights = generate_behavioral_insights(df, streak_summary["habit_metrics"], routines)

        if not insights:
            st.info("No insights triggered yet. Log additional days to reveal behavioral patterns.")
        else:
            for ins in insights:
                border_color = (
                    "var(--db-accent)" if ins["type"] == "success"
                    else ("var(--db-warning)" if ins["type"] == "warning" else "var(--db-info)")
                )
                icon_display = ins.get("icon", "•")
                st.markdown(
                    f"""
                    <div class="db-card" style="border-left: 4px solid {border_color}; margin-bottom: 0.85rem; padding: 1.15rem 1.35rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                            <span style="font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: {border_color};">
                                {icon_display} {ins['category']}
                            </span>
                            <span class="db-stat-badge" style="background: var(--db-surface); border-color: var(--db-border); color: var(--db-text-muted);">
                                {ins['metric_proof']}
                            </span>
                        </div>
                        <div style="font-size: 1.15rem; font-weight: 700; margin: 0.35rem 0; color: var(--db-text);">
                            {ins['title']}
                        </div>
                        <div style="font-size: 0.94rem; color: var(--db-text-secondary); line-height: 1.5;">
                            {ins['message']}
                        </div>
                        <div style="margin-top: 0.75rem; padding: 0.6rem 0.85rem; background: var(--db-accent-light); border-radius: 6px; font-size: 0.88rem; color: var(--db-accent); font-weight: 500;">
                            <strong>Suggested Step:</strong> {ins['action_step']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # -------------------------------------------------------------------------
    # TAB 3: Weekday Consistency Rhythm
    # -------------------------------------------------------------------------
    with tab_weekday:
        st.markdown("#### Weekday Consistency & Rhythm")
        st.caption("How your habit completion, study hours, sleep, and energy vary across days of the week.")

        st.plotly_chart(create_weekday_bar_chart(df_weekday, theme_mode), use_container_width=True)

        if not df_weekday.empty:
            st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
            st.markdown("##### Detailed Day-of-Week Averages")
            display_cols = {
                "weekday_name": "Day of Week",
                "total_days": "Tracked Days",
                "avg_completion_rate": "Avg Completion %",
                "avg_study_minutes": "Avg Study (Mins)",
                "avg_sleep_hours": "Avg Sleep (Hrs)",
                "avg_exercise_minutes": "Avg Exercise (Mins)",
                "avg_mood": "Avg Mood (1-5)",
                "avg_energy": "Avg Energy (1-5)"
            }
            renamed = df_weekday[[c for c in display_cols.keys() if c in df_weekday.columns]].rename(columns=display_cols)
            st.dataframe(renamed, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 4: Rolling Trends & Momentum
    # -------------------------------------------------------------------------
    with tab_trends:
        st.markdown("#### Consistency Momentum & Long-Term Trends")
        st.caption("7-day smoothing to filter daily variations and reveal genuine momentum shifts.")

        st.plotly_chart(create_completion_trend_chart(df_rolling, theme_mode), use_container_width=True)
        st.plotly_chart(create_lifestyle_trend_chart(df, theme_mode), use_container_width=True)


show_analytics_and_insights()
