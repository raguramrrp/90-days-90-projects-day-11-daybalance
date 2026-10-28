"""
DayBalance Desktop — Calendar & History Log Page
Displays daily habit execution timeline, completion percentages, and lifestyle journals.
"""

from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any

from database.repository import (
    get_habit_entries, get_habits, get_lifestyle_logs
)
from services.analytics_service import build_daily_analytics_dataframe
from desktop_app.components import ScrollableFrame


class CalendarPage(tk.Frame):
    def __init__(
        self,
        parent,
        profile: Dict[str, Any],
        palette: Dict[str, str],
        on_navigate: Callable[[str], None],
        **kwargs
    ):
        p = palette
        self.p = p
        self.profile = profile
        self.on_navigate = on_navigate

        super().__init__(parent, bg=p["bg"], **kwargs)

        self.scroll = ScrollableFrame(self, bg=p["bg"])
        self.scroll.pack(fill="both", expand=True)
        self.content = self.scroll.scrollable_content

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        p = self.p
        bg = p["bg"]
        surface = p["surface"]
        border = p["border"]
        pad_x = 24

        hdr = tk.Frame(self.content, bg=bg, padx=pad_x, pady=18)
        hdr.pack(fill="x")

        tk.Label(
            hdr,
            text="Calendar & Daily History Log",
            font=("Segoe UI", 16, "bold"),
            fg=p["text_primary"],
            bg=bg
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Chronological record of habit consistency, focus blocks, and lifestyle journal entries",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=bg
        ).pack(anchor="w", pady=(2, 0))

        content_box = tk.Frame(self.content, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        content_box.pack(fill="both", expand=True, padx=pad_x, pady=(0, 24))

        tk.Label(
            content_box,
            text="HISTORICAL EXECUTION RECORDS (LAST 30 DAYS)",
            font=("Segoe UI", 9, "bold"),
            fg=p["accent"],
            bg=surface
        ).pack(anchor="w", pady=(0, 10))

        self.history_tree_frame = tk.Frame(content_box, bg=surface)
        self.history_tree_frame.pack(fill="both", expand=True)

    def refresh(self):
        p_id = self.profile.get("id", 1)
        today = date.today()
        start_date = (today - timedelta(days=30)).isoformat()

        habits = get_habits(p_id, include_archived=False)
        entries = get_habit_entries(p_id, start_date=start_date)
        lifestyle = get_lifestyle_logs(p_id, start_date=start_date)
        df = build_daily_analytics_dataframe(habits, entries, lifestyle, start_date=start_date)

        for w in self.history_tree_frame.winfo_children():
            w.destroy()

        if df.empty:
            tk.Label(
                self.history_tree_frame,
                text="No historical entries found for this profile.",
                font=("Segoe UI", 9),
                fg=self.p["text_muted"],
                bg=self.p["surface"],
                pady=20
            ).pack()
            return

        cols = ("date", "weekday", "habits_done", "completion_rate", "sleep", "study", "exercise", "mood")
        tree = ttk.Treeview(self.history_tree_frame, columns=cols, show="headings", height=12)
        tree.heading("date", text="Date")
        tree.heading("weekday", text="Day")
        tree.heading("habits_done", text="Completed")
        tree.heading("completion_rate", text="Rate (%)")
        tree.heading("sleep", text="Sleep (hrs)")
        tree.heading("study", text="Focus (mins)")
        tree.heading("exercise", text="Exercise (mins)")
        tree.heading("mood", text="Mood (1-5)")

        tree.column("date", width=100)
        tree.column("weekday", width=90)
        tree.column("habits_done", width=90)
        tree.column("completion_rate", width=90)
        tree.column("sleep", width=90)
        tree.column("study", width=90)
        tree.column("exercise", width=100)
        tree.column("mood", width=80)

        # Reverse to show most recent days on top
        for _, row in df.iloc[::-1].iterrows():
            d_val = str(row.get("date", ""))
            wk_val = str(row.get("weekday_name", ""))
            done_val = f"{int(row.get('completed_habits_count', 0))}"
            rate_val = f"{float(row.get('completion_rate', 0.0)):.1f}%"
            sleep_val = f"{float(row.get('sleep_hours', 0.0)):.1f}" if row.get("sleep_hours") else "--"
            study_val = f"{int(row.get('study_minutes', 0))}" if row.get("study_minutes") else "--"
            ex_val = f"{int(row.get('exercise_minutes', 0))}" if row.get("exercise_minutes") else "--"
            mood_val = f"{int(row.get('mood_score', 0))}" if row.get("mood_score") else "--"

            tree.insert("", "end", values=(
                d_val, wk_val, done_val, rate_val, sleep_val, study_val, ex_val, mood_val
            ))

        tree.pack(fill="both", expand=True)
