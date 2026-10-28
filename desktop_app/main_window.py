"""
DayBalance Desktop Application Main Window
Orchestrates sidebar navigation, theme management, workspace page routing,
and keyboard shortcuts into a cohesive, native desktop experience.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

from database.migrations import init_db
from database.repository import get_profiles, update_profile
from services.demo_data_service import seed_demo_profile
from desktop_app.theme import apply_theme, PALETTES
from desktop_app.navigation import TopNavigationBar, NavigationSidebar

# Page imports
from desktop_app.pages.dashboard_page import DashboardPage
from desktop_app.pages.checkin_page import CheckinPage
from desktop_app.pages.habits_page import HabitsPage
from desktop_app.pages.calendar_page import CalendarPage
from desktop_app.pages.analytics_page import AnalyticsPage
from desktop_app.pages.experiments_page import ExperimentsPage
from desktop_app.pages.timer_page import TimerPage
from desktop_app.pages.wearables_page import WearablesPage
from desktop_app.pages.settings_page import SettingsPage


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Ensure database tables are initialized
        init_db()

        # Ensure active profile exists
        profiles = get_profiles()
        if not profiles:
            seed_demo_profile()
            profiles = get_profiles()

        self.current_profile = profiles[0] if profiles else {"id": 1, "name": "Alex Morgan", "theme_preference": "dark"}
        # Default to dark mode matching the approved design concept
        self.current_theme = "dark"

        # Window Configuration
        self.title("DayBalance — Behavioral Habit Analytics & Health Wearable Tracker")
        self.geometry("1240x800")
        self.minsize(1020, 660)

        # Apply Theme
        self.palette = apply_theme(self, self.current_theme)

        # Assemble Interface Layout
        self._build_layout()
        self._bind_shortcuts()

        # Start on Consistency Overview (Dashboard)
        self.navigate_to("dashboard")

    def _build_layout(self):
        # Top-level Container
        self.container = tk.Frame(self, bg=self.palette["bg"])
        self.container.pack(fill="both", expand=True)

        # Full-Width Top Navigation Bar (from the approved proposed design mockup)
        self.top_navbar = TopNavigationBar(
            self.container,
            on_navigate=self.navigate_to,
            on_toggle_theme=self._toggle_theme,
            palette=self.palette,
            profile_name=self.current_profile.get("name", "Alex Morgan"),
            current_theme=self.current_theme
        )
        self.top_navbar.pack(side="top", fill="x")

        # Alias for backward compatibility with tests
        self.sidebar = self.top_navbar

        # Full-Width Main Content Workspace
        self.workspace = tk.Frame(self.container, bg=self.palette["bg"])
        self.workspace.pack(side="bottom", fill="both", expand=True)

        # Initialize all pages inside workspace
        self.pages: Dict[str, tk.Frame] = {}

        self.pages["dashboard"] = DashboardPage(
            self.workspace,
            profile=self.current_profile,
            palette=self.palette,
            on_navigate=self.navigate_to,
            on_toggle_theme=self._toggle_theme
        )
        self.pages["checkin"] = CheckinPage(
            self.workspace,
            profile=self.current_profile,
            palette=self.palette,
            on_navigate=self.navigate_to
        )
        self.pages["habits"] = HabitsPage(
            self.workspace,
            profile=self.current_profile,
            palette=self.palette,
            on_navigate=self.navigate_to
        )
        self.pages["calendar"] = CalendarPage(
            self.workspace,
            profile=self.current_profile,
            palette=self.palette,
            on_navigate=self.navigate_to
        )
        self.pages["analytics"] = AnalyticsPage(
            self.workspace,
            profile=self.current_profile,
            palette=self.palette,
            on_navigate=self.navigate_to
        )
        self.pages["experiments"] = ExperimentsPage(
            self.workspace,
            profile=self.current_profile,
            palette=self.palette,
            on_navigate=self.navigate_to
        )
        self.pages["timer"] = TimerPage(
            self.workspace,
            profile=self.current_profile,
            palette=self.palette,
            on_navigate=self.navigate_to
        )
        self.pages["wearables"] = WearablesPage(
            self.workspace,
            profile=self.current_profile,
            palette=self.palette,
            on_navigate=self.navigate_to
        )
        self.pages["settings"] = SettingsPage(
            self.workspace,
            profile=self.current_profile,
            palette=self.palette,
            on_navigate=self.navigate_to,
            on_theme_changed=self.change_theme,
            on_profile_switched=self.switch_profile
        )

    def navigate_to(self, page_key: str):
        """Switches active workspace page."""
        for key, p in self.pages.items():
            if key == page_key:
                p.pack(fill="both", expand=True)
                if hasattr(p, "refresh"):
                    p.refresh()
            else:
                p.pack_forget()

        self.sidebar.active_key = page_key
        self.sidebar._update_styles()

    def _toggle_theme(self):
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.change_theme(new_theme)

    def change_theme(self, new_theme: str):
        """Dynamically re-applies theme across application."""
        if new_theme not in PALETTES or new_theme == self.current_theme:
            return
        self.current_theme = new_theme
        self.palette = apply_theme(self, new_theme)
        update_profile(self.current_profile["id"], theme_preference=new_theme)

        # Rebuild layout to apply color updates
        cur_page = self.sidebar.active_key
        self.container.destroy()
        self._build_layout()
        self.navigate_to(cur_page)

    def switch_profile(self, new_profile: Dict[str, Any]):
        """Switches active user profile and reloads application state."""
        self.current_profile = new_profile
        cur_page = self.sidebar.active_key
        self.container.destroy()
        self._build_layout()
        self.navigate_to(cur_page)

    def _bind_shortcuts(self):
        """Configure standard desktop productivity keyboard shortcuts."""
        self.bind("<F5>", lambda e: self._shortcut_refresh())
        self.bind("<Control-Key-1>", lambda e: self.navigate_to("dashboard"))
        self.bind("<Control-Key-2>", lambda e: self.navigate_to("checkin"))
        self.bind("<Control-Key-3>", lambda e: self.navigate_to("habits"))
        self.bind("<Control-Key-4>", lambda e: self.navigate_to("calendar"))
        self.bind("<Control-Key-5>", lambda e: self.navigate_to("analytics"))
        self.bind("<Control-Key-6>", lambda e: self.navigate_to("experiments"))
        self.bind("<Control-Key-7>", lambda e: self.navigate_to("timer"))
        self.bind("<Control-Key-8>", lambda e: self.navigate_to("wearables"))
        self.bind("<Control-Key-9>", lambda e: self.navigate_to("settings"))

    def _shortcut_refresh(self):
        active = self.sidebar.active_key
        page = self.pages.get(active)
        if page and hasattr(page, "refresh"):
            page.refresh()
