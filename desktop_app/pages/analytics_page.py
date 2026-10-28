"""
DayBalance Desktop — Analytics & Insights Page
Provides empirical statistical correlations, weekday completion patterns, and deterministic behavioral insights.
"""

from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any

from database.repository import get_habit_entries, get_habits, get_lifestyle_logs, get_routines
from services.analytics_service import (
    build_daily_analytics_dataframe, calculate_relationship,
    compute_weekday_performance
)
from services.insights_service import generate_behavioral_insights
from desktop_app.components import ScrollableFrame, StatCard


class AnalyticsPage(tk.Frame):
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
        pad_x = 24

        hdr = tk.Frame(self.content, bg=bg, padx=pad_x, pady=18)
        hdr.pack(fill="x")

        tk.Label(
            hdr,
            text="Analytics & Consistency Intelligence",
            font=("Segoe UI", 16, "bold"),
            fg=p["text_primary"],
            bg=bg
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Habit synergy patterns, weekday rhythms, and personalized behavioral findings",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=bg
        ).pack(anchor="w", pady=(2, 0))

        # 1. Habit Synergy Cards (Plain English, Zero Formulae)
        sec_corr = tk.Frame(self.content, bg=bg, padx=pad_x, pady=6)
        sec_corr.pack(fill="x")

        tk.Label(sec_corr, text="LIFESTYLE SYNERGIES & HABIT IMPACT", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=bg).pack(anchor="w")

        self.corr_cards_frame = tk.Frame(self.content, bg=bg, padx=pad_x, pady=0)
        self.corr_cards_frame.pack(fill="x")
        self.corr_cards_frame.columnconfigure((0, 1, 2), weight=1)

        self.card_c1 = StatCard(self.corr_cards_frame, "Sleep vs Focus Minutes", "Strong Synergy", "Consistent sleep increases daily study time", palette=p)
        self.card_c1.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.card_c2 = StatCard(self.corr_cards_frame, "Exercise vs Energy", "High Vitality", "Daily workouts sustain daytime energy", palette=p, accent_color=p["warning"])
        self.card_c2.grid(row=0, column=1, sticky="nsew", padx=3)

        self.card_c3 = StatCard(self.corr_cards_frame, "Mood vs Habit Rate", "Positive Alignment", "Positive mood strengthens habit completion", palette=p, accent_color=p["info"])
        self.card_c3.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        # 2. Weekday Performance Breakdown
        sec_week = tk.Frame(self.content, bg=bg, padx=pad_x, pady=8)
        sec_week.pack(fill="x")

        tk.Label(sec_week, text="WEEKDAY CONSISTENCY PROFILE", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=bg).pack(anchor="w")

        self.weekday_frame = tk.Frame(self.content, bg=p["surface"], highlightbackground=p["border"], highlightthickness=1, padx=pad_x)
        self.weekday_frame.pack(fill="x", padx=pad_x, pady=(0, 18))

        # 3. Deterministic Behavioral Insights
        sec_ins = tk.Frame(self.content, bg=bg, padx=pad_x, pady=8)
        sec_ins.pack(fill="x")

        tk.Label(sec_ins, text="DETERMINISTIC BEHAVIORAL FINDINGS", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=bg).pack(anchor="w")

        self.insights_frame = tk.Frame(self.content, bg=bg, padx=pad_x, pady=0)
        self.insights_frame.pack(fill="x")

    def refresh(self):
        p_id = self.profile.get("id", 1)
        today = date.today()
        start_date = (today - timedelta(days=60)).isoformat()

        habits = get_habits(p_id, include_archived=False)
        entries = get_habit_entries(p_id, start_date=start_date)
        lifestyle = get_lifestyle_logs(p_id, start_date=start_date)
        df = build_daily_analytics_dataframe(habits, entries, lifestyle, start_date=start_date)

        # 1. Compute correlations
        c1 = calculate_relationship(df, "sleep_hours", "study_minutes")
        c2 = calculate_relationship(df, "exercise_minutes", "energy_score")
        c3 = calculate_relationship(df, "mood_score", "completion_rate")

        def fmt_synergy(c_res, positive_desc, inverse_desc):
            r = c_res.get("pearson_r")
            if r is not None:
                pct = int(round(abs(r) * 100))
                if r >= 0.4:
                    return f"+{pct}% Strong Synergy", positive_desc
                elif r >= 0.2:
                    return f"+{pct}% Positive Boost", positive_desc
                elif r <= -0.2:
                    return f"-{pct}% Inverse Trend", inverse_desc
                else:
                    return "Neutral Pattern", "Both routines operate independently"
            return "Collecting Data", "Log more days to reveal habit connection"

        v1, s1 = fmt_synergy(c1, "Consistent sleep significantly boosts daily focus time", "Sleep and study minutes fluctuate separately")
        v2, s2 = fmt_synergy(c2, "Morning workouts sustain high daytime energy levels", "Workouts and energy operate independently")
        v3, s3 = fmt_synergy(c3, "Higher daily mood directly strengthens habit completion", "Mood and completion fluctuate independently")

        self.card_c1.update_data(v1, s1)
        self.card_c2.update_data(v2, s2)
        self.card_c3.update_data(v3, s3)

        # 2. Weekday breakdown
        for w in self.weekday_frame.winfo_children():
            w.destroy()

        w_df = compute_weekday_performance(df)
        if not w_df.empty:
            cols = ("day", "rate", "focus", "sleep", "exercise")
            tree = ttk.Treeview(self.weekday_frame, columns=cols, show="headings", height=7)
            tree.heading("day", text="Day of Week")
            tree.heading("rate", text="Habit Rate (%)")
            tree.heading("focus", text="Avg Focus (mins)")
            tree.heading("sleep", text="Avg Sleep (hrs)")
            tree.heading("exercise", text="Avg Exercise (mins)")

            tree.column("day", width=120)
            tree.column("rate", width=120)
            tree.column("focus", width=130)
            tree.column("sleep", width=130)
            tree.column("exercise", width=140)

            for _, row in w_df.iterrows():
                rate_val = f"{float(row.get('avg_completion_rate', 0.0)):.1f}%"
                focus_val = f"{int(round(float(row.get('avg_study_minutes', 0.0))))}m"
                sleep_val = f"{float(row.get('avg_sleep_hours', 0.0)):.1f}h"
                ex_val = f"{int(round(float(row.get('avg_exercise_minutes', 0.0))))}m"
                tree.insert("", "end", values=(
                    row.get("weekday_name", ""),
                    rate_val,
                    focus_val,
                    sleep_val,
                    ex_val
                ))
            tree.pack(fill="x", pady=8)

        # 3. Behavioral Insights
        for w in self.insights_frame.winfo_children():
            w.destroy()

        from services.streaks_service import calculate_profile_streak_summary
        streak_sum = calculate_profile_streak_summary(habits, entries, today)
        routines = get_routines(p_id)
        insights = generate_behavioral_insights(df, streak_sum.get("habit_metrics", []), routines)

        if not insights:
            tk.Label(self.insights_frame, text="Log 7+ consecutive days to generate personalized behavioral insights.", font=("Segoe UI", 9), fg=self.p["text_muted"], bg=self.p["bg"]).pack(anchor="w")
        else:
            for ins in insights:
                card = tk.Frame(self.insights_frame, bg=self.p["surface"], highlightbackground=self.p["border"], highlightthickness=1, padx=14, pady=10)
                card.pack(fill="x", pady=4)

                tk.Label(card, text=ins.get("title", "Insight"), font=("Segoe UI", 9, "bold"), fg=self.p["accent"], bg=self.p["surface"]).pack(anchor="w")
                tk.Label(card, text=ins.get("body", ""), font=("Segoe UI", 8), fg=self.p["text_secondary"], bg=self.p["surface"]).pack(anchor="w", pady=(2, 0))
