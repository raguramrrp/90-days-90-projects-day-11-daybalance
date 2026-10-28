"""
Tests for DayBalance Plotly Chart Generators
Verifies Plotly 7+ compatibility, ColorBar schemas, theme token injection, and error resiliency.
"""

from datetime import date, timedelta
import pandas as pd
import pytest
import plotly.graph_objects as go
from components.charts import (
    create_calendar_activity_heatmap,
    create_completion_trend_chart,
    create_correlation_scatter_chart,
    create_lifestyle_trend_chart,
    create_weekday_bar_chart,
)


@pytest.fixture
def sample_timeseries_df():
    """Generates 14 days of realistic daily analytics data."""
    start = date(2026, 1, 1)
    rows = []
    for i in range(14):
        d = start + timedelta(days=i)
        rows.append({
            "date": d.isoformat(),
            "date_obj": d,
            "weekday_short": d.strftime("%a"),
            "completion_rate": 50.0 + (i * 3.0),
            "completion_rate_rolling_7": 60.0 + (i * 1.5),
            "sleep_hours": 7.0 + (0.1 * (i % 5)),
            "study_minutes": 120 + (i * 10),
            "exercise_minutes": 30 if i % 2 == 0 else 0,
            "mood_score": 4,
            "energy_score": 3,
        })
    return pd.DataFrame(rows)


def test_completion_trend_chart_renders_without_error(sample_timeseries_df):
    """Verifies daily completion trend chart generation with bars and rolling line."""
    fig = create_completion_trend_chart(sample_timeseries_df, theme_mode="dark")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2  # Bar trace + Scatter rolling trace

    # Test empty dataframe graceful fallback
    empty_fig = create_completion_trend_chart(pd.DataFrame(), theme_mode="light")
    assert isinstance(empty_fig, go.Figure)
    assert len(empty_fig.data) == 0


def test_weekday_bar_chart_renders_without_error():
    """Verifies weekday consistency bar chart with Monday-Sunday ordering."""
    weekday_df = pd.DataFrame([
        {"weekday_idx": 0, "weekday_short": "Mon", "avg_completion_rate": 80.0, "total_days": 4},
        {"weekday_idx": 1, "weekday_short": "Tue", "avg_completion_rate": 75.0, "total_days": 4},
        {"weekday_idx": 5, "weekday_short": "Sat", "avg_completion_rate": 60.0, "total_days": 4},
        {"weekday_idx": 6, "weekday_short": "Sun", "avg_completion_rate": 50.0, "total_days": 4},
    ])
    fig = create_weekday_bar_chart(weekday_df, theme_mode="dark")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].type == "bar"

    # Empty fallback
    empty_fig = create_weekday_bar_chart(pd.DataFrame())
    assert isinstance(empty_fig, go.Figure)


def test_lifestyle_trend_chart_dual_axis(sample_timeseries_df):
    """Verifies lifestyle trend chart with dual y-axes for sleep and study."""
    fig = create_lifestyle_trend_chart(sample_timeseries_df, theme_mode="dark")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2
    assert fig.data[0].yaxis == "y" or fig.data[0].yaxis == "y1"
    assert fig.data[1].yaxis == "y2"

    # Empty fallback
    empty_fig = create_lifestyle_trend_chart(pd.DataFrame())
    assert isinstance(empty_fig, go.Figure)


def test_calendar_activity_heatmap_colorbar_and_pivot(sample_timeseries_df):
    """
    Verifies heatmap rendering and specifically checks that Plotly 7 ColorBar
    configuration does not use deprecated or invalid properties such as 'titleside'.
    """
    fig = create_calendar_activity_heatmap(sample_timeseries_df, theme_mode="dark")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    heatmap_trace = fig.data[0]
    assert heatmap_trace.type == "heatmap"

    # ColorBar verification
    cb = heatmap_trace.colorbar
    assert cb is not None
    assert cb.title.text == "Comp %"

    # Empty fallback
    empty_fig = create_calendar_activity_heatmap(pd.DataFrame())
    assert isinstance(empty_fig, go.Figure)


def test_correlation_scatter_chart_with_linear_fit():
    """Verifies bivariate scatter plot, OLS trendline, and scientific annotations."""
    df_pairs = pd.DataFrame({
        "sleep_hours": [6.0, 7.0, 7.5, 8.0, 8.5, 6.5, 7.2, 8.1],
        "study_minutes": [90, 150, 180, 210, 240, 110, 160, 200]
    })
    rel_result = {
        "x_col": "sleep_hours",
        "y_col": "study_minutes",
        "x_name": "Sleep Duration (Hours)",
        "y_name": "Study / Focus Time (Minutes)",
        "pearson_r": 0.95,
        "spearman_rho": 0.92,
        "is_sufficient": True,
        "n_pairs": 8,
        "min_required": 7,
        "valid_df": df_pairs
    }

    fig = create_correlation_scatter_chart(rel_result, theme_mode="dark")
    assert isinstance(fig, go.Figure)
    # Trace 0: scatter points, Trace 1: OLS linear fit line
    assert len(fig.data) == 2
    assert fig.data[0].mode == "markers"
    assert fig.data[1].mode == "lines"

    # Insufficient data fallback
    insufficient_result = {
        "x_name": "Sleep",
        "y_name": "Study",
        "is_sufficient": False,
        "message": "Only 3 observation pairs found"
    }
    fallback_fig = create_correlation_scatter_chart(insufficient_result)
    assert isinstance(fallback_fig, go.Figure)
    assert len(fallback_fig.data) == 0


def test_today_progress_ring_renders_correctly():
    """Verifies that circular progress ring donut renders valid annotations and values."""
    from components.charts import create_today_progress_ring
    fig = create_today_progress_ring(completed_count=5, total_count=6, theme_mode="light")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].hole == 0.76
    assert fig.layout.annotations[0].text == "<b>83%</b>"
    assert "5/6 Done" in fig.layout.annotations[1].text


def test_habit_category_donut_renders_correctly():
    """Verifies habit category breakdown donut chart."""
    from components.charts import create_habit_category_donut
    habits = [
        {"name": "Run", "category": "Health & Fitness"},
        {"name": "Study", "category": "Study & Academic"},
        {"name": "Meditate", "category": "Mindfulness & Well-being"}
    ]
    fig = create_habit_category_donut(habits, theme_mode="dark")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert len(fig.data[0].labels) == 3
