"""
Tests for DayBalance UI Theme System, Visual Tokens & Navigation Helpers
Verifies Sage Green & Warm Ivory palette tokens, Light mode default, and component rendering.
"""

import pytest
from components.theme import get_current_theme, get_theme_tokens, set_current_theme
from config import THEME_TOKENS
from components.metric_cards import render_status_badge


def test_theme_tokens_contain_sage_and_ivory_palette():
    """Verifies that light and dark theme tokens adhere to the modern delightful habit tracker aesthetic."""
    light_tokens = get_theme_tokens("light")
    assert light_tokens["bg_primary"] == "#F8FAFC"  # Fresh Slate canvas
    assert light_tokens["accent"] == "#10B981"      # Vibrant Emerald Mint
    assert light_tokens["text_primary"] == "#0F172A"  # Deep Charcoal Typography
    assert light_tokens["plotly_template"] == "plotly_white"

    dark_tokens = get_theme_tokens("dark")
    assert dark_tokens["bg_primary"] == "#0B0F17"   # Midnight Obsidian
    assert dark_tokens["accent"] == "#34D399"       # Luminous Emerald Mint
    assert dark_tokens["plotly_template"] == "plotly_dark"


def test_status_badge_generation():
    """Verifies that render_status_badge produces valid HTML with accessible symbols."""
    completed_badge = render_status_badge({
        "status": "completed",
        "label": "Completed",
        "symbol": "✓",
        "badge_class": "status-success"
    })
    assert "✓" in completed_badge
    assert "Completed" in completed_badge
    assert "status-success" in completed_badge

    rest_badge = render_status_badge({
        "status": "rest_day",
        "label": "Rest Day",
        "symbol": "R",
        "badge_class": "status-rest"
    })
    assert "R" in rest_badge
    assert "Rest Day" in rest_badge


def test_category_badge_and_streak_strip():
    """Verifies that category pastel tags and Everyday 7-day squircle chains render properly."""
    from components.metric_cards import get_category_badge_html, render_everyday_streak_strip

    tag = get_category_badge_html("Health & Fitness")
    assert "db-cat-health" in tag
    assert "Health & Fitness" in tag

    days = [
        {"day_short": "Mon", "status": "completed", "label": "Completed"},
        {"day_short": "Tue", "status": "rest_day", "label": "Rest Day"},
        {"day_short": "Wed", "status": "pending", "label": "Unlogged"}
    ]
    strip = render_everyday_streak_strip("Water Hydration", days)
    assert "Water Hydration" in strip
    assert "db-pill-done" in strip
    assert "db-pill-rest" in strip


def test_navigation_bar_contrast_and_config():
    """Verifies that Streamlit config uses light base theme and dark text color for high contrast."""
    from pathlib import Path
    config_file = Path(__file__).resolve().parent.parent / ".streamlit" / "config.toml"
    assert config_file.exists()
    content = config_file.read_text(encoding="utf-8")
    assert 'base = "light"' in content
    assert 'textColor = "#0F172A"' in content
    assert 'primaryColor = "#059669"' in content
