"""
DayBalance UI Metric Cards, Strip & Heading Helpers
Renders minimal typography-led metric strips, compact headings, and accessible badges.
"""

from typing import Any, Dict, List, Optional
import streamlit as st
from components.theme import get_current_theme, get_theme_tokens


def render_header(title: str, subtitle: Optional[str] = None) -> None:
    """Renders compact, context-rich page title and metadata."""
    st.markdown(
        f"""
        <div class="db-header-container">
            <h1 class="db-header-title">{title}</h1>
            {f'<p class="db-header-subtitle">{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(
    label: str,
    value: Any,
    subtext: Optional[str] = None,
    delta: Optional[str] = None,
    delta_color: str = "normal"
) -> None:
    """
    Renders an individual minimal typography-led metric box with accessible contrast.
    """
    tokens = get_theme_tokens(get_current_theme())
    delta_html = ""
    if delta:
        d_color = tokens["status_success"] if delta_color == "positive" else (
            tokens["status_danger"] if delta_color == "negative" else tokens["text_secondary"]
        )
        delta_html = f"<span style='color: {d_color}; font-size: 0.82rem; font-weight: 600; margin-left: 0.4rem;'>{delta}</span>"

    st.markdown(
        f"""
        <div class="db-card" style="margin-bottom: 0.5rem; padding: 0.9rem 1.1rem;">
            <div class="db-metric-label">{label}</div>
            <div class="db-metric-val">{value}{delta_html}</div>
            {f'<div class="db-metric-sub">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_strip(metrics: List[Dict[str, Any]]) -> None:
    """
    Renders a unified, typography-led metric strip across the viewport.
    Each item in `metrics` is a dict with: 'label', 'value', optional 'subtext', and optional 'delta'.
    """
    tokens = get_theme_tokens(get_current_theme())
    items_html = ""
    for m in metrics:
        delta_html = ""
        if m.get("delta"):
            d_color = tokens["status_success"] if m.get("delta_color") == "positive" else (
                tokens["status_danger"] if m.get("delta_color") == "negative" else tokens["text_secondary"]
            )
            delta_html = f"<span style='color: {d_color}; font-size: 0.8rem; font-weight: 600; margin-left: 0.4rem;'>{m['delta']}</span>"

        subtext_html = f"<div class=\"db-metric-sub\">{m['subtext']}</div>" if m.get("subtext") else ""

        items_html += f"""
        <div class="db-editorial-metric">
            <div class="db-metric-label">{m['label']}</div>
            <div class="db-metric-val">{m['value']}{delta_html}</div>
            {subtext_html}
        </div>
        """

    st.markdown(
        f"""
        <div class="db-metric-strip">
            {items_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def get_category_badge_html(category: str) -> str:
    """Returns a styled pastel category pill tag for habit cards."""
    cat_lower = category.lower() if category else "custom"
    cls = "db-cat-custom"
    if "health" in cat_lower or "fitness" in cat_lower:
        cls = "db-cat-health"
    elif "study" in cat_lower or "academic" in cat_lower:
        cls = "db-cat-study"
    elif "mind" in cat_lower or "well" in cat_lower or "meditat" in cat_lower:
        cls = "db-cat-mind"
    elif "productiv" in cat_lower or "deep" in cat_lower:
        cls = "db-cat-work"
    elif "move" in cat_lower or "active" in cat_lower:
        cls = "db-cat-active"
    elif "creat" in cat_lower or "person" in cat_lower:
        cls = "db-cat-creative"

    return f'<span class="db-cat-tag {cls}">{category}</span>'


def render_bento_stat_card(
    label: str,
    value: Any,
    subtext: Optional[str] = None,
    badge: Optional[str] = None,
    icon: Optional[str] = None,
    icon_bg: str = "#E6F7F0",
    icon_color: str = "#059669"
) -> None:
    """
    Renders a Bento Stat Card matching the exact DayBalance design mockup.
    Includes squircle icon on the left, uppercase label, bold metric, and metadata.
    """
    icon_html = f'<div class="db-bento-icon" style="background: {icon_bg}; color: {icon_color};">{icon}</div>' if icon else ""
    sub_html = f'<div class="db-bento-sub">{subtext}</div>' if subtext else ""
    badge_html = f"<span class='db-stat-badge'>{badge}</span>" if badge else ""

    st.markdown(
        f'<div class="db-bento-card">{icon_html}<div class="db-bento-content"><div style="display: flex; justify-content: space-between; align-items: center;"><span class="db-bento-label">{label}</span>{badge_html}</div><div class="db-bento-value">{value}</div>{sub_html}</div></div>',
        unsafe_allow_html=True
    )


def render_everyday_streak_strip(habit_name: str, days_data: List[Dict[str, Any]]) -> str:
    """
    Renders a 7-day squircle consistency chain HTML snippet.
    Constructs clean, single-line HTML without indentation to prevent CommonMark code block conversion.
    """
    pills_html = ""
    for d in days_data:
        status = d.get("status", "pending")
        cls = "db-pill-pending"
        symbol = "·"
        if status == "completed":
            cls = "db-pill-done"
            symbol = "✓"
        elif status == "rest_day":
            cls = "db-pill-rest"
            symbol = "R"
        elif status == "missed":
            cls = "db-pill-missed"
            symbol = "×"

        pills_html += f'<div class="db-day-pill {cls}" title="{d.get("date", "")}: {d.get("day_short", "")} ({d.get("label", status)})">{symbol}</div>'

    return f'<div style="display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0.8rem; background: var(--db-secondary); border: 1px solid var(--db-border-subtle); border-radius: 8px; margin-bottom: 0.45rem;"><span style="font-size: 0.84rem; font-weight: 600; color: var(--db-text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 180px;">{habit_name}</span><div class="db-chain-container">{pills_html}</div></div>'


def render_status_badge(status_dict: Dict[str, Any]) -> str:
    """Returns an HTML badge string for displaying habit status with symbol and accessible label."""
    badge_cls = status_dict.get("badge_class", "status-pending")
    symbol = status_dict.get("symbol", "•")
    label = status_dict.get("label", "Unknown")
    return f'<span class="db-badge {badge_cls}" title="{label}">{symbol} {label}</span>'


def render_calendar_legend() -> None:
    """Renders accessible legend explaining habit completion status states."""
    st.markdown(
        """
        <div class="db-legend-container">
            <span style="font-weight: 600; color: var(--db-text); margin-right: 0.5rem;">Status Legend:</span>
            <div class="db-legend-item"><span class="db-badge status-success">✓ Completed</span></div>
            <div class="db-legend-item"><span class="db-badge status-warning">• Partial</span></div>
            <div class="db-legend-item"><span class="db-badge status-rest">R Rest Day</span></div>
            <div class="db-legend-item"><span class="db-badge status-skipped">— Skipped</span></div>
            <div class="db-legend-item"><span class="db-badge status-danger">× Missed</span></div>
            <div class="db-legend-item"><span class="db-badge status-pending">• Pending</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )
