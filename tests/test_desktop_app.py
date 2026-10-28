"""
Unit tests for DayBalance Native Desktop Application (Tkinter GUI).
Verifies window instantiation, page navigation, theme toggling, and data binding.
"""

from pathlib import Path
from desktop_app.main_window import MainWindow
from desktop_app.theme import PALETTES, apply_theme


def test_desktop_main_window_instantiation(test_db_path: Path):
    app = MainWindow()
    app.withdraw()

    # Verify window title
    assert "DayBalance" in app.title()

    # Verify all 9 pages exist
    expected_pages = [
        "dashboard", "checkin", "habits", "calendar",
        "analytics", "experiments", "timer", "wearables", "settings"
    ]
    for page_key in expected_pages:
        assert page_key in app.pages

    # Verify initial page is dashboard
    assert app.sidebar.active_key == "dashboard"

    # Verify page navigation
    app.navigate_to("checkin")
    assert app.sidebar.active_key == "checkin"

    app.navigate_to("habits")
    assert app.sidebar.active_key == "habits"

    app.navigate_to("wearables")
    assert app.sidebar.active_key == "wearables"

    # Verify theme switching
    app.change_theme("light")
    assert app.current_theme == "light"

    app.change_theme("dark")
    assert app.current_theme == "dark"

    app.destroy()


def test_desktop_theme_palettes():
    assert "dark" in PALETTES
    assert "light" in PALETTES
    for mode in ["dark", "light"]:
        p = PALETTES[mode]
        assert "bg" in p
        assert "surface" in p
        assert "accent" in p
        assert "text_primary" in p
        assert "border" in p
