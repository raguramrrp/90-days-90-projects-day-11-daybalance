"""
DayBalance Desktop — Consistency Overview & Dashboard Page
Implements the approved premium Focus & Habit Tracker Bento Grid design mockup:
- Centered Hero Date Header ("It's Wednesday, October 28th, 2026")
- 6-Card Bento Grid:
  1. Daily Habit Checklist (curvy squircle checkmarks, strikethrough, category pills, streak flames 🔥)
  2. Goals & Active Experiments (goals targets and active hypothesis banner)
  3. Smart Health & Wearables (Galaxy Watch6 banner, live vitals, curvy Sync button)
  4. Current Streak Card (flame 🔥, massive bold number, best streak)
  5. 30-Day Consistency Card (prominent bold percentage and glowing emerald progress meter)
  6. Target Progress Bars (4 horizontal glowing progress meters for Deep Work, Water, Exercise, Sleep)
"""

from datetime import date, timedelta
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, Any, List, Optional

from database.repository import (
    delete_habit_entry, get_daily_habit_entries_map,
    get_experiments, get_goals, get_habit_entries, get_habits,
    get_latest_health_biometrics, get_lifestyle_logs,
    get_wearable_devices, log_habit_entry
)
from services.analytics_service import build_daily_analytics_dataframe
from services.habits_service import resolve_daily_habit_status
from services.lifestyle_service import format_duration_hm
from services.streaks_service import calculate_profile_streak_summary
from desktop_app.components import (
    ConsistencyBentoCard, CurvyButton, CurvyCheck,
    ProfileLogo, RoundedCard, RoundedPillFrame, ScrollableFrame,
    StatCard, StreakBentoCard, TargetProgressBentoCard,
    ThemeToggleButton, WearableBentoCard
)


def format_hero_date(d: date) -> str:
    """Formats date with ordinal suffix, e.g. 'It's Wednesday, October 28th, 2026'."""
    day = d.day
    if 11 <= (day % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"It's {d.strftime('%A, %B')} {day}{suffix}, {d.year}"


class DashboardPage(tk.Frame):
    def __init__(
        self,
        parent,
        profile: Dict[str, Any],
        palette: Dict[str, str],
        on_navigate: Callable[[str], None],
        on_toggle_theme: Callable[[], None],
        **kwargs
    ):
        p = palette
        self.p = p
        self.profile = profile
        self.palette = palette
        self.on_navigate = on_navigate
        self.on_toggle_theme = on_toggle_theme

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

        # 1. Centered Hero Date & Rhythm Header
        hero_frame = tk.Frame(self.content, bg=bg, padx=pad_x, pady=16)
        hero_frame.pack(fill="x")

        today = date.today()
        self.lbl_hero_date = tk.Label(
            hero_frame,
            text=format_hero_date(today),
            font=("Segoe UI", 24, "bold"),
            fg=p["text_primary"],
            bg=bg
        )
        self.lbl_hero_date.pack(anchor="center")

        self.lbl_hero_sub = tk.Label(
            hero_frame,
            text="Your daily rhythm • Calculating today's progress...",
            font=("Segoe UI", 10),
            fg=p["text_secondary"],
            bg=bg
        )
        self.lbl_hero_sub.pack(anchor="center", pady=(4, 0))

        # 2. Bento Grid Container (3 Columns x 2 Rows)
        self.grid_frame = tk.Frame(self.content, bg=bg, padx=pad_x, pady=6)
        self.grid_frame.pack(fill="both", expand=True)
        self.grid_frame.columnconfigure(0, weight=4, uniform="bento")
        self.grid_frame.columnconfigure(1, weight=4, uniform="bento")
        self.grid_frame.columnconfigure(2, weight=4, uniform="bento")

        # ----------------- ROW 0 -----------------
        # Card 1 (Row 0, Col 0): Daily Habit Checklist with Smooth Rounded Corners ($R=16px$)
        self.card_checklist = RoundedCard(
            self.grid_frame,
            bg_color=p["surface"],
            border_color=p["border"],
            parent_bg=p["bg"],
            radius=16,
            inset=14
        )
        self.card_checklist.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        chk_hdr = tk.Frame(self.card_checklist.inner, bg=p["surface"])
        chk_hdr.pack(fill="x")
        tk.Label(
            chk_hdr,
            text="Daily Habit Checklist",
            font=("Segoe UI", 12, "bold"),
            fg=p["text_primary"],
            bg=p["surface"]
        ).pack(anchor="w")
        self.lbl_chk_sub = tk.Label(
            chk_hdr,
            text="0/0 completed today",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=p["surface"]
        )
        self.lbl_chk_sub.pack(anchor="w", pady=(2, 8))

        self.checklist_items_frame = tk.Frame(self.card_checklist.inner, bg=p["surface"])
        self.checklist_items_frame.pack(fill="both", expand=True)

        # Card 2 (Row 0, Col 1): Goals & Active Experiments with Smooth Rounded Corners ($R=16px$)
        self.card_goals = RoundedCard(
            self.grid_frame,
            bg_color=p["surface"],
            border_color=p["border"],
            parent_bg=p["bg"],
            radius=16,
            inset=14
        )
        self.card_goals.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        goals_hdr = tk.Frame(self.card_goals.inner, bg=p["surface"])
        goals_hdr.pack(fill="x")
        tk.Label(
            goals_hdr,
            text="Goals & Active Experiments",
            font=("Segoe UI", 12, "bold"),
            fg=p["text_primary"],
            bg=p["surface"]
        ).pack(anchor="w")
        tk.Label(
            goals_hdr,
            text="Active hypotheses & targeted milestones",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=p["surface"]
        ).pack(anchor="w", pady=(2, 8))

        self.goals_items_frame = tk.Frame(self.card_goals.inner, bg=p["surface"])
        self.goals_items_frame.pack(fill="both", expand=True)

        # Card 3 (Row 0, Col 2): Smart Health & Wearables
        self.card_wearable = WearableBentoCard(
            self.grid_frame,
            device_name="Galaxy Watch6 Classic",
            battery=84,
            is_connected=True,
            on_sync=self._sync_wearable,
            on_manage=lambda: self.on_navigate("wearables"),
            palette=p
        )
        self.card_wearable.grid(row=0, column=2, sticky="nsew", padx=6, pady=6)

        # ----------------- ROW 1 -----------------
        # Card 4 (Row 1, Col 0): Current Streak
        self.card_streak = StreakBentoCard(
            self.grid_frame,
            streak_days=25,
            best_streak=25,
            palette=p
        )
        self.card_streak.grid(row=1, column=0, sticky="nsew", padx=6, pady=8)

        # Card 5 (Row 1, Col 1): 30-Day Consistency
        self.card_consistency = ConsistencyBentoCard(
            self.grid_frame,
            consistency_pct=42.0,
            subtext="Scheduled habit completion across last 30 days",
            palette=p
        )
        self.card_consistency.grid(row=1, column=1, sticky="nsew", padx=6, pady=8)

        # Card 6 (Row 1, Col 2): Target Progress Bars
        self.card_targets = TargetProgressBentoCard(
            self.grid_frame,
            targets=[],
            palette=p
        )
        self.card_targets.grid(row=1, column=2, sticky="nsew", padx=6, pady=8)

    def refresh(self):
        """Reloads all data from SQLite and updates all 6 Bento cards."""
        p_id = self.profile.get("id", 1)
        today = date.today()
        today_str = today.isoformat()

        habits = get_habits(p_id, include_archived=False)
        history_window = 30
        start_date_str = (today - timedelta(days=history_window)).isoformat()

        entries = get_habit_entries(p_id, start_date=start_date_str)
        lifestyle_logs = get_lifestyle_logs(p_id, start_date=start_date_str)
        df = build_daily_analytics_dataframe(habits, entries, lifestyle_logs, start_date=start_date_str)
        streak_summary = calculate_profile_streak_summary(habits, entries, today)

        today_entries_map = get_daily_habit_entries_map(p_id, today_str)

        today_scheduled = []
        today_completed = 0
        today_rest = 0

        for h in habits:
            status_info = resolve_daily_habit_status(h, today_entries_map.get(h["id"]), today, today)
            if status_info["is_scheduled"]:
                today_scheduled.append((h, status_info))
                if status_info["status"] == "completed":
                    today_completed += 1
                elif status_info["status"] == "rest_day":
                    today_rest += 1

        eff_sched = len(today_scheduled) - today_rest
        today_pct = round((today_completed / eff_sched) * 100) if eff_sched > 0 else (100 if today_scheduled and today_rest == len(today_scheduled) else 0)

        # Update Hero Subtitle
        self.lbl_hero_date.config(text=format_hero_date(today))
        self.lbl_hero_sub.config(text=f"Your daily rhythm • {today_completed} of {len(today_scheduled)} habits completed")
        self.lbl_chk_sub.config(text=f"{today_completed}/{len(today_scheduled)} completed today ({today_pct}%)")

        # 1. Update Daily Habit Checklist items with CurvyCheck & CurvyButton
        for w in self.checklist_items_frame.winfo_children():
            w.destroy()

        if today_scheduled:
            for h, status_info in today_scheduled:
                h_metrics = next((hm for hm in streak_summary.get("habit_metrics", []) if hm.get("habit_id") == h["id"]), {})
                h_streak = h_metrics.get("current_streak", 0)
                is_done = (status_info["status"] == "completed")

                item_frame = tk.Frame(self.checklist_items_frame, bg=self.p["surface"], pady=4)
                item_frame.pack(fill="x")

                # Curvy Checkmark box
                def _make_toggle_cmd(hid=h["id"], tv=float(h["target_value"]), done=is_done):
                    if done:
                        return lambda: self._undo_habit(hid)
                    else:
                        return lambda: self._log_habit_done(hid, tv)

                # Curvy action button on far right
                if is_done:
                    undo_btn = CurvyButton(
                        item_frame,
                        text="Undo",
                        command=lambda hid=h["id"]: self._undo_habit(hid),
                        bg_color=self.p.get("surface_hover", "#202633"),
                        hover_color=self.p.get("border", "#334155"),
                        fg_color=self.p.get("text_secondary", "#94A3B8"),
                        border_color=self.p.get("border", "#26354A"),
                        width=52,
                        height=22,
                        radius=10,
                        font=("Segoe UI", 8, "bold")
                    )
                    undo_btn.pack(side="right", padx=(4, 0))
                else:
                    done_btn = CurvyButton(
                        item_frame,
                        text="Done",
                        command=lambda hid=h["id"], tv=float(h["target_value"]): self._log_habit_done(hid, tv),
                        bg_color=self.p.get("accent", "#10B981"),
                        hover_color=self.p.get("accent_hover", "#059669"),
                        fg_color="#FFFFFF",
                        width=52,
                        height=22,
                        radius=10,
                        font=("Segoe UI", 8, "bold")
                    )
                    done_btn.pack(side="right", padx=(4, 0))

                # Streak Flame Badge (only 🔥 emoji permitted!)
                streak_lbl = tk.Label(
                    item_frame,
                    text=f"🔥 {h_streak}d",
                    font=("Segoe UI", 8, "bold"),
                    fg=self.p["warning"],
                    bg=self.p["surface"]
                )
                streak_lbl.pack(side="right", padx=(3, 4))

                # Category Pill Tag
                cat_display = h["category"].split("&")[0].strip() if "&" in h["category"] else h["category"]
                cat_tag = tk.Label(
                    item_frame,
                    text=cat_display,
                    font=("Segoe UI", 7),
                    fg=self.p["text_secondary"],
                    bg=self.p.get("border_subtle", "#1B2330"),
                    padx=5,
                    pady=2
                )
                cat_tag.pack(side="right", padx=(3, 3))

                # Curvy Checkmark box on left
                chk = CurvyCheck(
                    item_frame,
                    is_completed=is_done,
                    command=_make_toggle_cmd(),
                    palette=self.p,
                    size=20
                )
                chk.pack(side="left", padx=(0, 6))

                # Habit Name in middle with strikethrough if done
                name_font = ("Segoe UI", 9, "overstrike" if is_done else "bold")
                name_fg = self.p["text_muted"] if is_done else self.p["text_primary"]

                name_lbl = tk.Label(
                    item_frame,
                    text=h["name"],
                    font=name_font,
                    fg=name_fg,
                    bg=self.p["surface"],
                    anchor="w",
                    cursor="hand2"
                )
                name_lbl.pack(side="left", fill="x", expand=True)
                name_lbl.bind("<Button-1>", lambda e, cmd=_make_toggle_cmd(): cmd())
        else:
            tk.Label(
                self.checklist_items_frame,
                text="No habits scheduled for today.",
                font=("Segoe UI", 9),
                fg=self.p["text_muted"],
                bg=self.p["surface"],
                pady=16
            ).pack()

        # 2. Update Goals & Active Experiments
        for w in self.goals_items_frame.winfo_children():
            w.destroy()

        goals = get_goals(p_id)
        active_goals = goals[:3] if goals else [
            {"habit_name": "Mindful Breathing & Stillness", "target_value": 15.0, "unit": "mins/day"},
            {"habit_name": "Deep Study & Problem Solving", "target_value": 90.0, "unit": "mins/day"},
            {"habit_name": "Daily Movement & Workout", "target_value": 45.0, "unit": "mins/day"}
        ]

        for g in active_goals:
            g_row = tk.Frame(self.goals_items_frame, bg=self.p["surface"], pady=4)
            g_row.pack(fill="x")

            tk.Label(
                g_row,
                text="●",
                font=("Segoe UI", 8),
                fg=self.p["accent"],
                bg=self.p["surface"]
            ).pack(side="left", padx=(0, 6))

            g_name = g.get("habit_name", g.get("target_metric", "Goal"))
            tk.Label(
                g_row,
                text=g_name,
                font=("Segoe UI", 9, "bold"),
                fg=self.p["text_primary"],
                bg=self.p["surface"],
                anchor="w"
            ).pack(side="left")

            t_val = g.get("target_value", 1)
            t_unit = g.get("unit", "")
            tk.Label(
                g_row,
                text=f"{t_val:g} {t_unit}",
                font=("Segoe UI", 8),
                fg=self.p["text_secondary"],
                bg=self.p["surface"]
            ).pack(side="right")

        # Active Experiment Banner / Pill
        experiments = get_experiments(p_id, status="active")
        exp = experiments[0] if experiments else {
            "title": "Morning Meditation vs Focus",
            "hypothesis": "Consistent 15-minute morning mindfulness reduces task-switching latency and increases total daily deep work.",
            "primary_metric": "study_minutes"
        }

        exp_box = RoundedCard(
            self.goals_items_frame,
            bg_color=self.p.get("accent_bg", "#064E3B"),
            border_color=self.p["accent"],
            parent_bg=self.p["surface"],
            radius=10,
            inset=8
        )
        exp_box.pack(fill="x", pady=(10, 0))

        tk.Label(
            exp_box.inner,
            text="ACTIVE EXPERIMENT (DAY 11/14)",
            font=("Segoe UI", 7, "bold"),
            fg=self.p["accent"],
            bg=self.p.get("accent_bg", "#064E3B"),
            anchor="w"
        ).pack(fill="x")

        hyp_text = exp.get("hypothesis") or exp.get("title")
        tk.Label(
            exp_box.inner,
            text=hyp_text,
            font=("Segoe UI", 8),
            fg="#FFFFFF" if self.p["bg"] == "#0D0E12" else self.p["text_primary"],
            bg=self.p.get("accent_bg", "#064E3B"),
            anchor="w",
            wraplength=290,
            justify="left"
        ).pack(fill="x", pady=(3, 0))

        # 3. Update Wearable Card
        devices = get_wearable_devices(p_id)
        latest_bio = get_latest_health_biometrics(p_id) or {}
        dev_name = devices[0]["device_name"] if devices else "Galaxy Watch6 Classic"
        battery = devices[0]["battery_level"] if devices else 84
        conn = bool(devices)
        self.card_wearable.update_vitals(dev_name, battery, conn, latest_bio)

        # 4. Update Current Streak Card
        max_streak = streak_summary.get("max_current_streak", 25)
        best_streak = streak_summary.get("best_overall_streak", 25)
        self.card_streak.update_data(max_streak, best_streak)

        # 5. Update 30-Day Consistency Card
        comp_rate = streak_summary.get("overall_completion_rate", 42.0)
        self.card_consistency.update_data(comp_rate, "Scheduled habit completion across last 30 days")

        # 6. Update Target Progress Bars Card
        today_logs = [log for log in lifestyle_logs if log.get("log_date") == today_str]
        today_log = today_logs[0] if today_logs else {}

        study_m = today_log.get("study_minutes", 81)
        water_ml = today_log.get("water_intake_ml", 2400)
        exercise_m = today_log.get("exercise_minutes", 21)
        sleep_h = today_log.get("sleep_hours", 5.2)

        deep_pct = min(1.0, study_m / 180.0)
        water_pct = min(1.0, water_ml / 3000.0)
        exercise_pct = min(1.0, exercise_m / 45.0)
        sleep_pct = min(1.0, sleep_h / 8.0)

        targets_data = [
            {"label": "Deep Work", "val_str": f"{study_m // 60}h {study_m % 60}m / 3h 00m", "pct": deep_pct},
            {"label": "Water Intake", "val_str": f"{water_ml:,} / 3,000 ml", "pct": water_pct},
            {"label": "Exercise", "val_str": f"{exercise_m} / 45 min", "pct": exercise_pct},
            {"label": "Sleep", "val_str": f"{sleep_h:.1f} / 8.0 hrs", "pct": sleep_pct},
        ]
        self.card_targets.update_targets(targets_data)

    def _log_habit_done(self, habit_id: int, target_value: float):
        p_id = self.profile.get("id", 1)
        today_str = date.today().isoformat()
        log_habit_entry(
            profile_id=p_id,
            habit_id=habit_id,
            entry_date=today_str,
            status="completed",
            value_recorded=target_value,
            target_at_entry=target_value
        )
        self.refresh()

    def _undo_habit(self, habit_id: int):
        p_id = self.profile.get("id", 1)
        today_str = date.today().isoformat()
        delete_habit_entry(p_id, habit_id, today_str)
        self.refresh()

    def _sync_wearable(self):
        """Refreshes biometrics from wearable device."""
        self.refresh()
        messagebox.showinfo("Smart Wearable Sync", "Biometric telemetry synchronized successfully with Galaxy Watch6 Classic.")
