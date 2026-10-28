"""
DayBalance Desktop — Daily Check-in Page
Enables quick completion of daily habits alongside lifestyle metrics (sleep, study, exercise, mood, energy).
"""

from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any, List

from database.repository import (
    get_daily_habit_entries_map, get_habits,
    get_lifestyle_log, log_habit_entry, log_lifestyle
)
from services.habits_service import resolve_daily_habit_status
from desktop_app.components import ScrollableFrame


class CheckinPage(tk.Frame):
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

        self.habit_vars: Dict[int, tk.BooleanVar] = {}
        self.habit_val_entries: Dict[int, ttk.Entry] = {}

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        p = self.p
        bg = p["bg"]
        surface = p["surface"]
        border = p["border"]
        pad_x = 24

        # Header
        hdr = tk.Frame(self.content, bg=bg, padx=pad_x, pady=18)
        hdr.pack(fill="x")

        tk.Label(
            hdr,
            text="Daily Check-in & Lifestyle Journal",
            font=("Segoe UI", 16, "bold"),
            fg=p["text_primary"],
            bg=bg
        ).pack(anchor="w")

        today = date.today()
        tk.Label(
            hdr,
            text=f"Log your daily habit execution, recovery, and cognitive focus for {today.strftime('%A, %B %d, %Y')}",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=bg
        ).pack(anchor="w", pady=(2, 0))

        # Two Column Layout: Left Habits, Right Lifestyle Metrics
        cols_frame = tk.Frame(self.content, bg=bg, padx=pad_x, pady=0)
        cols_frame.pack(fill="both", expand=True)
        cols_frame.columnconfigure(0, weight=3)
        cols_frame.columnconfigure(1, weight=2)

        # Left Column: Scheduled Habits
        left_box = tk.Frame(cols_frame, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(
            left_box,
            text="TODAY'S SCHEDULED HABITS",
            font=("Segoe UI", 9, "bold"),
            fg=p["accent"],
            bg=surface
        ).pack(anchor="w", pady=(0, 10))

        self.habits_list_frame = tk.Frame(left_box, bg=surface)
        self.habits_list_frame.pack(fill="both", expand=True)

        # Right Column: Lifestyle Biometrics & Notes
        right_box = tk.Frame(cols_frame, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        right_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(
            right_box,
            text="LIFESTYLE & RECOVERY BIOMETRICS",
            font=("Segoe UI", 9, "bold"),
            fg=p["accent"],
            bg=surface
        ).pack(anchor="w", pady=(0, 12))

        # Sleep Hours
        tk.Label(right_box, text="Sleep Duration (Hours):", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.ent_sleep = ttk.Entry(right_box)
        self.ent_sleep.insert(0, "7.8")
        self.ent_sleep.pack(fill="x", pady=(2, 8))

        # Sleep Quality (1-5)
        tk.Label(right_box, text="Sleep Quality (1 - 5):", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.ent_sleep_q = ttk.Combobox(right_box, values=["1", "2", "3", "4", "5"], state="readonly")
        self.ent_sleep_q.set("4")
        self.ent_sleep_q.pack(fill="x", pady=(2, 8))

        # Study Minutes
        tk.Label(right_box, text="Study / Deep Focus Minutes:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.ent_study = ttk.Entry(right_box)
        self.ent_study.insert(0, "120")
        self.ent_study.pack(fill="x", pady=(2, 8))

        # Exercise Minutes & Type
        tk.Label(right_box, text="Exercise Minutes:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.ent_exercise = ttk.Entry(right_box)
        self.ent_exercise.insert(0, "40")
        self.ent_exercise.pack(fill="x", pady=(2, 8))

        tk.Label(right_box, text="Exercise Type:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.ent_ex_type = ttk.Combobox(right_box, values=["Running", "Gym / Resistance", "Cycling", "Walking", "Yoga", "Swimming"], state="readonly")
        self.ent_ex_type.set("Running")
        self.ent_ex_type.pack(fill="x", pady=(2, 8))

        # Mood (1-5) & Energy (1-5)
        m_row = tk.Frame(right_box, bg=surface)
        m_row.pack(fill="x", pady=(2, 8))
        m_row.columnconfigure(0, weight=1)
        m_row.columnconfigure(1, weight=1)

        m_c1 = tk.Frame(m_row, bg=surface)
        m_c1.grid(row=0, column=0, sticky="w", padx=(0, 4))
        tk.Label(m_c1, text="Mood (1-5):", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.ent_mood = ttk.Combobox(m_c1, values=["1", "2", "3", "4", "5"], state="readonly", width=8)
        self.ent_mood.set("4")
        self.ent_mood.pack(fill="x", pady=(2, 0))

        m_c2 = tk.Frame(m_row, bg=surface)
        m_c2.grid(row=0, column=1, sticky="e", padx=(4, 0))
        tk.Label(m_c2, text="Energy (1-5):", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.ent_energy = ttk.Combobox(m_c2, values=["1", "2", "3", "4", "5"], state="readonly", width=8)
        self.ent_energy.set("4")
        self.ent_energy.pack(fill="x", pady=(2, 0))

        # Reflection Notes
        tk.Label(right_box, text="Daily Reflection Note:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.txt_notes = tk.Text(right_box, height=3, bg=p["input_bg"], fg=p["input_fg"], font=("Segoe UI", 8), highlightbackground=border, highlightthickness=1)
        self.txt_notes.pack(fill="x", pady=(2, 14))

        # Save Button
        ttk.Button(
            right_box,
            text="Save Daily Check-in",
            style="Accent.TButton",
            command=self._save_checkin
        ).pack(fill="x")

    def refresh(self):
        p_id = self.profile.get("id", 1)
        today = date.today()
        today_str = today.isoformat()

        habits = get_habits(p_id, include_archived=False)
        today_map = get_daily_habit_entries_map(p_id, today_str)

        for w in self.habits_list_frame.winfo_children():
            w.destroy()

        self.habit_vars.clear()
        self.habit_val_entries.clear()

        scheduled = []
        for h in habits:
            st_info = resolve_daily_habit_status(h, today_map.get(h["id"]), today, today)
            if st_info["is_scheduled"]:
                scheduled.append((h, st_info))

        if not scheduled:
            tk.Label(
                self.habits_list_frame,
                text="No habits scheduled for today.",
                font=("Segoe UI", 9),
                fg=self.p["text_muted"],
                bg=self.p["surface"],
                pady=16
            ).pack()
            return

        for h, st_info in scheduled:
            hid = h["id"]
            is_done = (st_info["status"] == "completed")

            row = tk.Frame(self.habits_list_frame, bg=self.p["surface"], pady=6)
            row.pack(fill="x")

            var = tk.BooleanVar(value=is_done)
            self.habit_vars[hid] = var

            chk = tk.Checkbutton(
                row,
                variable=var,
                bg=self.p["surface"],
                activebackground=self.p["surface"],
                highlightthickness=0
            )
            chk.pack(side="left")

            info = tk.Frame(row, bg=self.p["surface"])
            info.pack(side="left", fill="x", expand=True, padx=8)

            tk.Label(info, text=h["name"], font=("Segoe UI", 9, "bold"), fg=self.p["text_primary"], bg=self.p["surface"]).pack(anchor="w")
            tk.Label(info, text=f"Target: {h['target_value']:g} {h['unit']} • {h['category']}", font=("Segoe UI", 8), fg=self.p["text_muted"], bg=self.p["surface"]).pack(anchor="w")

            ent = ttk.Entry(row, width=8)
            cur_entry = today_map.get(hid)
            val_to_show = cur_entry.get("value_recorded", h["target_value"]) if cur_entry else h["target_value"]
            ent.insert(0, f"{val_to_show:g}")
            ent.pack(side="right")
            self.habit_val_entries[hid] = ent

            tk.Frame(self.habits_list_frame, bg=self.p["border_subtle"], height=1).pack(fill="x")

        # Load existing lifestyle log if present
        log = get_lifestyle_log(p_id, today_str)
        if log:
            self.ent_sleep.delete(0, "end")
            self.ent_sleep.insert(0, str(log.get("sleep_hours") or "7.5"))
            self.ent_sleep_q.set(str(log.get("sleep_quality") or "4"))
            self.ent_study.delete(0, "end")
            self.ent_study.insert(0, str(log.get("study_minutes") or "120"))
            self.ent_exercise.delete(0, "end")
            self.ent_exercise.insert(0, str(log.get("exercise_minutes") or "30"))
            if log.get("exercise_type"):
                self.ent_ex_type.set(log["exercise_type"])
            self.ent_mood.set(str(log.get("mood_score") or "4"))
            self.ent_energy.set(str(log.get("energy_score") or "4"))
            self.txt_notes.delete("1.0", "end")
            if log.get("reflection_notes"):
                self.txt_notes.insert("1.0", log["reflection_notes"])

    def _save_checkin(self):
        p_id = self.profile.get("id", 1)
        today_str = date.today().isoformat()

        # 1. Save habit entries
        habits = get_habits(p_id, include_archived=False)
        for h in habits:
            hid = h["id"]
            if hid in self.habit_vars:
                is_completed = self.habit_vars[hid].get()
                val_str = self.habit_val_entries[hid].get().strip()
                try:
                    val_rec = float(val_str)
                except ValueError:
                    val_rec = float(h["target_value"])

                if is_completed:
                    log_habit_entry(
                        profile_id=p_id,
                        habit_id=hid,
                        entry_date=today_str,
                        status="completed",
                        value_recorded=val_rec,
                        target_at_entry=float(h["target_value"])
                    )

        # 2. Save lifestyle log
        try:
            sleep_h = float(self.ent_sleep.get().strip() or "7.5")
            sleep_q = int(self.ent_sleep_q.get() or "4")
            study_m = int(self.ent_study.get().strip() or "120")
            ex_m = int(self.ent_exercise.get().strip() or "0")
            ex_type = self.ent_ex_type.get() or None
            mood_s = int(self.ent_mood.get() or "4")
            energy_s = int(self.ent_energy.get() or "4")
            notes = self.txt_notes.get("1.0", "end").strip() or None

            log_lifestyle(
                profile_id=p_id,
                log_date=today_str,
                sleep_hours=sleep_h,
                sleep_quality=sleep_q,
                study_minutes=study_m,
                focus_sessions_count=max(1, study_m // 45),
                exercise_minutes=ex_m,
                exercise_type=ex_type,
                mood_score=mood_s,
                energy_score=energy_s,
                reflection_notes=notes
            )
            messagebox.showinfo("Success", "Daily Check-in successfully recorded!")
            self.on_navigate("dashboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save check-in: {e}")
