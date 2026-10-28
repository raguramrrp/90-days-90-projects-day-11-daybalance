"""
DayBalance Desktop — Habits & Routines Configuration Page
Create, configure, inspect, and manage habits with schedule-aware frequency rules.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any

from database.repository import archive_habit, create_habit, get_habits
from desktop_app.components import ScrollableFrame


class HabitsPage(tk.Frame):
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
            text="Habits & Routines Management",
            font=("Segoe UI", 16, "bold"),
            fg=p["text_primary"],
            bg=bg
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Configure schedule-aware routines, protected rest days, and quantitative daily targets",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=bg
        ).pack(anchor="w", pady=(2, 0))

        # Main Layout: Top Creation Card, Bottom Table
        create_box = tk.Frame(self.content, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        create_box.pack(fill="x", padx=pad_x, pady=(0, 18))

        tk.Label(
            create_box,
            text="CREATE NEW HABIT",
            font=("Segoe UI", 9, "bold"),
            fg=p["accent"],
            bg=surface
        ).pack(anchor="w", pady=(0, 10))

        form_grid = tk.Frame(create_box, bg=surface)
        form_grid.pack(fill="x")
        form_grid.columnconfigure((0, 1, 2, 3), weight=1)

        # Name
        tk.Label(form_grid, text="Habit Name:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).grid(row=0, column=0, sticky="w", padx=4)
        self.ent_name = ttk.Entry(form_grid)
        self.ent_name.grid(row=1, column=0, sticky="ew", padx=4, pady=(2, 8))

        # Category
        tk.Label(form_grid, text="Category:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).grid(row=0, column=1, sticky="w", padx=4)
        self.cmb_cat = ttk.Combobox(form_grid, values=["Deep Work", "Health & Fitness", "Mindfulness", "Learning", "Daily Routine"], state="readonly")
        self.cmb_cat.set("Deep Work")
        self.cmb_cat.grid(row=1, column=1, sticky="ew", padx=4, pady=(2, 8))

        # Frequency
        tk.Label(form_grid, text="Frequency:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).grid(row=0, column=2, sticky="w", padx=4)
        self.cmb_freq = ttk.Combobox(form_grid, values=["daily", "weekdays", "weekends"], state="readonly")
        self.cmb_freq.set("daily")
        self.cmb_freq.grid(row=1, column=2, sticky="ew", padx=4, pady=(2, 8))

        # Target & Unit
        tk.Label(form_grid, text="Target & Unit:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).grid(row=0, column=3, sticky="w", padx=4)
        tu_frame = tk.Frame(form_grid, bg=surface)
        tu_frame.grid(row=1, column=3, sticky="ew", padx=4, pady=(2, 8))
        self.ent_target = ttk.Entry(tu_frame, width=6)
        self.ent_target.insert(0, "1")
        self.ent_target.pack(side="left")
        self.ent_unit = ttk.Entry(tu_frame)
        self.ent_unit.insert(0, "session")
        self.ent_unit.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Create Button
        ttk.Button(
            create_box,
            text="Add Habit to Profile",
            style="Accent.TButton",
            command=self._create_habit
        ).pack(anchor="e", pady=(6, 0))

        # Table of Active Habits
        list_box = tk.Frame(self.content, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        list_box.pack(fill="both", expand=True, padx=pad_x, pady=(0, 24))

        tk.Label(
            list_box,
            text="ACTIVE HABIT CONFIGURATIONS",
            font=("Segoe UI", 9, "bold"),
            fg=p["accent"],
            bg=surface
        ).pack(anchor="w", pady=(0, 10))

        self.habits_tree_frame = tk.Frame(list_box, bg=surface)
        self.habits_tree_frame.pack(fill="both", expand=True)

    def refresh(self):
        p_id = self.profile.get("id", 1)
        habits = get_habits(p_id, include_archived=False)

        for w in self.habits_tree_frame.winfo_children():
            w.destroy()

        if not habits:
            tk.Label(
                self.habits_tree_frame,
                text="No active habits configured. Use the form above to add your first habit.",
                font=("Segoe UI", 9),
                fg=self.p["text_muted"],
                bg=self.p["surface"],
                pady=20
            ).pack()
            return

        cols = ("name", "category", "frequency", "target", "action")
        tree = ttk.Treeview(self.habits_tree_frame, columns=cols, show="headings", height=max(6, len(habits)))
        tree.heading("name", text="Habit Name")
        tree.heading("category", text="Category")
        tree.heading("frequency", text="Frequency")
        tree.heading("target", text="Target")
        tree.heading("action", text="Status")

        tree.column("name", width=220)
        tree.column("category", width=140)
        tree.column("frequency", width=110)
        tree.column("target", width=120)
        tree.column("action", width=100)

        for h in habits:
            tree.insert("", "end", iid=str(h["id"]), values=(
                h["name"],
                h["category"],
                str(h.get("frequency", "daily") or "daily").capitalize(),
                f"{h['target_value']:g} {h['unit']}",
                "Active"
            ))

        tree.pack(fill="both", expand=True)

        # Context action button
        def on_archive():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Select Habit", "Please click on a habit row to archive it.")
                return
            h_id = int(sel[0])
            archive_habit(h_id, p_id)
            self.refresh()

        ttk.Button(
            self.habits_tree_frame,
            text="Archive Selected Habit",
            style="Secondary.TButton",
            command=on_archive
        ).pack(anchor="e", pady=(10, 0))

    def _create_habit(self):
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showwarning("Validation Error", "Habit Name cannot be empty.")
            return

        cat = self.cmb_cat.get()
        freq = self.cmb_freq.get()
        try:
            target = float(self.ent_target.get().strip() or "1.0")
        except ValueError:
            target = 1.0
        unit = self.ent_unit.get().strip() or "times"

        p_id = self.profile.get("id", 1)
        create_habit(
            profile_id=p_id,
            name=name,
            category=cat,
            target_value=target,
            unit=unit,
            frequency=freq
        )
        self.ent_name.delete(0, "end")
        self.refresh()
        messagebox.showinfo("Success", f"Habit '{name}' created successfully!")
