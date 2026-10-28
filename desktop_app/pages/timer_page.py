"""
DayBalance Desktop — Focus Timer Page
Samsung One UI inspired countdown timer with quick presets, active ticking, and session logging.
"""

from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any

from database.repository import create_focus_session
from desktop_app.components import ScrollableFrame


class TimerPage(tk.Frame):
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

        self.total_seconds = 25 * 60
        self.remaining_seconds = self.total_seconds
        self.is_running = False
        self.timer_id = None
        self.start_timestamp = None

        self._build_ui()

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
            text="Deep Work Focus Timer",
            font=("Segoe UI", 16, "bold"),
            fg=p["text_primary"],
            bg=bg
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Distraction-free countdown interval timer inspired by Samsung One UI Clock",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=bg
        ).pack(anchor="w", pady=(2, 0))

        # Main Timer Center Panel
        timer_box = tk.Frame(self.content, bg=surface, highlightbackground=border, highlightthickness=1, padx=40, pady=32)
        timer_box.pack(fill="x", padx=pad_x, pady=(0, 24))

        # Preset Buttons Row
        preset_frame = tk.Frame(timer_box, bg=surface)
        preset_frame.pack(pady=(0, 24))

        presets = [("25m Pomodoro", 25), ("45m Deep Work", 45), ("60m Sprint", 60), ("15m Quick", 15)]
        for label, mins in presets:
            btn = ttk.Button(
                preset_frame,
                text=label,
                style="Secondary.TButton",
                command=lambda m=mins: self._set_duration(m)
            )
            btn.pack(side="left", padx=6)

        # Large Digital Countdown Display
        self.lbl_time = tk.Label(
            timer_box,
            text="25:00",
            font=("Segoe UI", 56, "bold"),
            fg=p["text_primary"],
            bg=surface
        )
        self.lbl_time.pack(pady=(8, 4))

        self.lbl_status = tk.Label(
            timer_box,
            text="Ready to immerse in deliberate practice",
            font=("Segoe UI", 9),
            fg=p["text_secondary"],
            bg=surface
        )
        self.lbl_status.pack(pady=(0, 24))

        # Controls Row
        ctrl_frame = tk.Frame(timer_box, bg=surface)
        ctrl_frame.pack(pady=(0, 16))

        self.btn_toggle = ttk.Button(
            ctrl_frame,
            text="Start Focus Block",
            style="Accent.TButton",
            command=self._toggle_timer
        )
        self.btn_toggle.pack(side="left", padx=6)

        self.btn_reset = ttk.Button(
            ctrl_frame,
            text="Reset Timer",
            style="Secondary.TButton",
            command=self._reset_timer
        )
        self.btn_reset.pack(side="left", padx=6)

        self.btn_log = ttk.Button(
            ctrl_frame,
            text="Log Completed Session",
            style="Secondary.TButton",
            command=self._log_session
        )
        self.btn_log.pack(side="left", padx=6)

    def _set_duration(self, minutes: int):
        self._stop_timer()
        self.total_seconds = minutes * 60
        self.remaining_seconds = self.total_seconds
        self._update_display()
        self.lbl_status.config(text=f"Target: {minutes} minutes focus session")

    def _toggle_timer(self):
        if self.is_running:
            self._stop_timer()
            self.btn_toggle.config(text="Resume Focus Block")
            self.lbl_status.config(text="Timer paused")
        else:
            self.is_running = True
            if self.start_timestamp is None:
                self.start_timestamp = datetime.now()
            self.btn_toggle.config(text="Pause Timer")
            self.lbl_status.config(text="Focus in progress... Stay deliberate")
            self._tick()

    def _tick(self):
        if self.is_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._update_display()
            self.timer_id = self.after(1000, self._tick)
        elif self.remaining_seconds <= 0:
            self._stop_timer()
            self.lbl_status.config(text="Focus session complete! Excellent focus.")
            messagebox.showinfo("Session Finished", "Focus interval completed! Great job.")
            self._log_session()

    def _stop_timer(self):
        self.is_running = False
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

    def _reset_timer(self):
        self._stop_timer()
        self.remaining_seconds = self.total_seconds
        self.start_timestamp = None
        self._update_display()
        self.btn_toggle.config(text="Start Focus Block")
        self.lbl_status.config(text="Timer reset. Ready when you are.")

    def _update_display(self):
        m = self.remaining_seconds // 60
        s = self.remaining_seconds % 60
        self.lbl_time.config(text=f"{m:02d}:{s:02d}")

    def _log_session(self):
        p_id = self.profile.get("id", 1)
        dur = max(1, (self.total_seconds - self.remaining_seconds) // 60)
        now_iso = datetime.now().isoformat()
        create_focus_session(
            profile_id=p_id,
            start_time=self.start_timestamp.isoformat() if self.start_timestamp else now_iso,
            end_time=now_iso,
            duration_minutes=dur,
            task_tag="Deliberate Focus",
            completed=1
        )
        messagebox.showinfo("Session Saved", f"Successfully logged {dur} minutes focus session to your profile!")
        self._reset_timer()
