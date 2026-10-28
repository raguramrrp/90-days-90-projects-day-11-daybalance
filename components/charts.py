"""
DayBalance Plotly Chart Visualizations
Produces interactive, accessible, responsive charts harmonized with the Sage Green & Warm Ivory palette.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from components.theme import get_plotly_layout, get_theme_tokens


def create_today_progress_ring(completed_count: int, total_count: int, theme_mode: Optional[str] = None) -> go.Figure:
    """
    Renders an Apple Fitness / Habitify style circular progress ring for today's habits.
    """
    tokens = get_theme_tokens(theme_mode)
    fig = go.Figure()

    pct = round((completed_count / total_count) * 100) if total_count > 0 else 0
    remaining = max(0, total_count - completed_count)

    fig.add_trace(go.Pie(
        values=[completed_count, remaining],
        labels=["Completed", "Remaining"],
        hole=0.76,
        direction="clockwise",
        sort=False,
        marker=dict(
            colors=[tokens["accent"], tokens["bg_secondary"]],
            line=dict(color=tokens["chart_bg"], width=2)
        ),
        textinfo="none",
        hoverinfo="label+value"
    ))

    layout_args = get_plotly_layout(theme_mode)
    layout_args.update({
        "showlegend": False,
        "annotations": [
            dict(
                text=f"<b>{pct}%</b>",
                x=0.5, y=0.55,
                font=dict(size=26, color=tokens["text_primary"]),
                showarrow=False
            ),
            dict(
                text=f"{completed_count}/{total_count} Done",
                x=0.5, y=0.38,
                font=dict(size=12, color=tokens["text_muted"]),
                showarrow=False
            )
        ],
        "margin": dict(l=10, r=10, t=10, b=10),
        "height": 190
    })
    fig.update_layout(**layout_args)
    return fig


def create_habit_category_donut(habits: List[Dict[str, Any]], theme_mode: Optional[str] = None) -> go.Figure:
    """
    Renders habit focus distribution by life area / category in soft pastel rings.
    """
    tokens = get_theme_tokens(theme_mode)
    fig = go.Figure()

    if not habits:
        fig.update_layout(
            **get_plotly_layout(theme_mode),
            title="Category Focus (No Habits)",
            height=260
        )
        return fig

    cat_counts: Dict[str, int] = {}
    for h in habits:
        cat = h.get("category", "Custom")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    labels = list(cat_counts.keys())
    values = list(cat_counts.values())

    category_palette = [
        "#10B981",  # Mint
        "#0284C7",  # Sky Blue
        "#8B5CF6",  # Violet
        "#F59E0B",  # Amber
        "#EC4899",  # Pink
        "#F97316",  # Orange
        "#64748B"   # Slate
    ]

    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.64,
        direction="clockwise",
        marker=dict(
            colors=category_palette[:len(labels)],
            line=dict(color=tokens["chart_bg"], width=2)
        ),
        textinfo="label+percent",
        textposition="outside",
        hovertemplate="<b>%{label}</b><br>%{value} Habit(s) (%{percent})<extra></extra>"
    ))

    layout_args = get_plotly_layout(theme_mode)
    layout_args.update({
        "title": "Habit Focus by Category",
        "showlegend": False,
        "margin": dict(l=25, r=25, t=40, b=25),
        "height": 260
    })
    fig.update_layout(**layout_args)
    return fig


def create_completion_trend_chart(df: pd.DataFrame, theme_mode: Optional[str] = None) -> go.Figure:
    """
    Renders daily habit completion trend as botanical sage bars with a smoothed 7-day rolling average line.
    """
    tokens = get_theme_tokens(theme_mode)
    fig = go.Figure()

    if df.empty or "date" not in df.columns:
        fig.update_layout(
            **get_plotly_layout(theme_mode),
            title="Daily Completion Trend (No Data Available)",
            height=300
        )
        return fig

    # Daily Completion Bars
    fig.add_trace(go.Bar(
        x=df["date"],
        y=df["completion_rate"],
        name="Daily Completion %",
        marker_color=tokens["accent"],
        opacity=0.75,
        hovertemplate="<b>%{x}</b><br>Completion: %{y:.1f}%<extra></extra>"
    ))

    # 7-Day Rolling Average Line if sufficient points
    if "completion_rate_rolling_7" in df.columns and df["completion_rate_rolling_7"].notna().sum() > 3:
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df["completion_rate_rolling_7"],
            name="7-Day Rolling Avg",
            mode="lines",
            line=dict(color=tokens["status_info"], width=2.5),
            hovertemplate="<b>%{x}</b><br>7-Day Avg: %{y:.1f}%<extra></extra>"
        ))

    layout_args = get_plotly_layout(theme_mode)
    layout_args.update({
        "title": "Daily Habit Completion Rate (%)",
        "yaxis": {"title": "Completion Rate (%)", "range": [0, 105], **layout_args.get("yaxis", {})},
        "xaxis": {"title": "Date", **layout_args.get("xaxis", {})},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        "height": 300
    })
    fig.update_layout(**layout_args)
    return fig


def create_weekday_bar_chart(weekday_df: pd.DataFrame, theme_mode: Optional[str] = None) -> go.Figure:
    """
    Compares average completion rates across Monday through Sunday.
    """
    tokens = get_theme_tokens(theme_mode)
    fig = go.Figure()

    if weekday_df.empty:
        fig.update_layout(
            **get_plotly_layout(theme_mode),
            title="Weekday vs Weekend Consistency (No Data)",
            height=300
        )
        return fig

    colors = [
        tokens["accent"] if row["weekday_idx"] < 5 else tokens["status_info"]
        for _, row in weekday_df.iterrows()
    ]

    fig.add_trace(go.Bar(
        x=weekday_df["weekday_short"],
        y=weekday_df["avg_completion_rate"],
        text=[f"{v:.0f}%" for v in weekday_df["avg_completion_rate"]],
        textposition="auto",
        marker_color=colors,
        hovertemplate="<b>%{x}</b><br>Avg Completion: %{y:.1f}%<br>Days Logged: %{customdata}<extra></extra>",
        customdata=weekday_df["total_days"]
    ))

    layout_args = get_plotly_layout(theme_mode)
    layout_args.update({
        "title": "Consistency Rhythm by Day of Week",
        "yaxis": {"title": "Avg Completion Rate (%)", "range": [0, 105], **layout_args.get("yaxis", {})},
        "xaxis": {"title": "Day of Week", **layout_args.get("xaxis", {})},
        "height": 300
    })
    fig.update_layout(**layout_args)
    return fig


def create_lifestyle_trend_chart(df: pd.DataFrame, theme_mode: Optional[str] = None) -> go.Figure:
    """
    Plots dual-axis relationship between Sleep Duration (Hours) and Study Time (Minutes).
    """
    tokens = get_theme_tokens(theme_mode)
    fig = go.Figure()

    if df.empty:
        fig.update_layout(**get_plotly_layout(theme_mode), title="Lifestyle Metrics Trend (No Data)", height=300)
        return fig

    # Sleep hours (Y1)
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["sleep_hours"],
        name="Sleep (Hours)",
        mode="lines+markers",
        line=dict(color=tokens["status_info"], width=2),
        marker=dict(size=4),
        yaxis="y1",
        hovertemplate="<b>%{x}</b><br>Sleep: %{y:.1f} hrs<extra></extra>"
    ))

    # Study minutes (Y2)
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["study_minutes"],
        name="Study / Focus (Mins)",
        mode="lines+markers",
        line=dict(color=tokens["accent"], width=2),
        marker=dict(size=4),
        yaxis="y2",
        hovertemplate="<b>%{x}</b><br>Study: %{y} mins<extra></extra>"
    ))

    layout_args = get_plotly_layout(theme_mode)
    layout_args.update({
        "title": "Sleep Duration & Focus Work Trend",
        "yaxis": {"title": "Sleep (Hours)", "side": "left", "showgrid": True, **layout_args.get("yaxis", {})},
        "yaxis2": {
            "title": "Study Time (Minutes)",
            "side": "right",
            "overlaying": "y",
            "showgrid": False,
            "tickfont": {"color": tokens["accent"]}
        },
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
        "height": 300
    })
    fig.update_layout(**layout_args)
    return fig


def create_correlation_scatter_chart(result: Dict[str, Any], theme_mode: Optional[str] = None) -> go.Figure:
    """
    Visualizes correlation pair scatter plot with smooth trendline and clean annotations.
    """
    tokens = get_theme_tokens(theme_mode)
    fig = go.Figure()

    if not result.get("is_sufficient", False) or "valid_df" not in result:
        fig.update_layout(
            **get_plotly_layout(theme_mode),
            title=f"Connection: {result.get('x_name')} & {result.get('y_name')} (More Data Needed)",
            height=320
        )
        return fig

    valid = result["valid_df"]
    x_col = result["x_col"]
    y_col = result["y_col"]
    x_vals = valid[x_col].values.astype(float)
    y_vals = valid[y_col].values.astype(float)

    # Scatter points
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="markers",
        name="Tracked Days",
        marker=dict(size=8, color=tokens["accent"], opacity=0.85, line=dict(color=tokens["border"], width=1)),
        hovertemplate=f"<b>{result['x_name']}</b>: %{{x}}<br><b>{result['y_name']}</b>: %{{y}}<extra></extra>"
    ))

    # Trendline if n >= 2 and variance > 0
    if len(x_vals) >= 2 and np.std(x_vals) > 0:
        poly = np.polyfit(x_vals, y_vals, 1)
        x_line = np.linspace(x_vals.min(), x_vals.max(), 50)
        y_line = poly[0] * x_line + poly[1]

        fig.add_trace(go.Scatter(
            x=x_line,
            y=y_line,
            mode="lines",
            name="Overall Habit Trend",
            line=dict(color=tokens["status_warning"], width=2.5, dash="dash")
        ))

    n = result.get("n_pairs", 0)
    direction = str(result.get("direction", "Positive")).lower()
    strength = str(result.get("strength", "Moderate")).lower()

    annotation_text = f"Pattern: {strength.title()} {direction.title()} Trend ({n} Tracked Days)"

    layout_args = get_plotly_layout(theme_mode)
    layout_args.update({
        "title": f"Habit Connection: {result['x_name']} & {result['y_name']}",
        "xaxis": {"title": result["x_name"], **layout_args.get("xaxis", {})},
        "yaxis": {"title": result["y_name"], **layout_args.get("yaxis", {})},
        "annotations": [{
            "xref": "paper", "yref": "paper",
            "x": 0.02, "y": 0.96,
            "text": annotation_text,
            "showarrow": False,
            "font": {"size": 11, "color": tokens["text_primary"], "family": "Inter, -apple-system, sans-serif"},
            "bgcolor": tokens["bg_card"],
            "bordercolor": tokens["border"],
            "borderwidth": 1,
            "borderpad": 5
        }],
        "height": 330
    })
    fig.update_layout(**layout_args)
    return fig


def create_calendar_activity_heatmap(df: pd.DataFrame, theme_mode: Optional[str] = None) -> go.Figure:
    """
    Renders an activity matrix heatmap across calendar weeks in Sage Green tones.
    """
    tokens = get_theme_tokens(theme_mode)
    fig = go.Figure()

    if df.empty or "date_obj" not in df.columns:
        fig.update_layout(**get_plotly_layout(theme_mode), title="Activity Matrix (No Data)", height=280)
        return fig

    # Enrich df with week number and weekday
    df_copy = df.copy()
    df_copy["iso_year"] = [d.isocalendar()[0] for d in df_copy["date_obj"]]
    df_copy["iso_week"] = [d.isocalendar()[1] for d in df_copy["date_obj"]]
    df_copy["weekday_short"] = df_copy["weekday_short"]

    # Pivot matrix: Weekday on Y, Date on X
    pivot = df_copy.pivot_table(
        index="weekday_short",
        columns="date",
        values="completion_rate",
        aggfunc="mean"
    )

    # Order weekdays Mon-Sun
    weekday_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    pivot = pivot.reindex([w for w in weekday_order if w in pivot.index])

    fig.add_trace(go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale=[
            [0.0, tokens["bg_secondary"]],
            [0.3, tokens["accent_light"]],
            [0.7, "rgba(78, 120, 94, 0.6)"],
            [1.0, tokens["accent"]]
        ],
        showscale=True,
        colorbar=dict(title=dict(text="Comp %")),
        hovertemplate="<b>%{x}</b> (%{y})<br>Completion: %{z:.1f}%<extra></extra>"
    ))

    layout_args = get_plotly_layout(theme_mode)
    layout_args.update({
        "title": "Daily Habit Completion Intensity Heatmap",
        "yaxis": {"title": "", "autorange": "reversed", **layout_args.get("yaxis", {})},
        "xaxis": {"title": "Calendar Date", "nticks": 10, **layout_args.get("xaxis", {})},
        "height": 280
    })
    fig.update_layout(**layout_args)
    return fig
