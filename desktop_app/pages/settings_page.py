"""
DayBalance Desktop — Settings & Profiles Configuration Page
Profile management, theme switching, demo data seeding, and JSON/CSV backup portability.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Callable, Dict, Any, List

from database.repository import (
    create_profile, get_profiles, update_profile
)
from services.backup_service import (
    export_entries_csv, export_profile_json,
    restore_profile_json
)
from services.demo_data_service import seed_demo_profile
from desktop_app.components import ScrollableFrame


class SettingsPage(tk.Frame):
    def __init__(
        self,
        parent,
        profile: Dict[str, Any],
        palette: Dict[str, str],
        on_navigate: Callable[[str], None],
        on_theme_changed: Callable[[str], None],
        on_profile_switched: Callable[[Dict[str, Any]], None],
        **kwargs
    ):
        p = palette
        self.p = p
        self.profile = profile
        self.on_navigate = on_navigate
        self.on_theme_changed = on_theme_changed
        self.on_profile_switched = on_profile_switched

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
            text="Settings & Profile Configuration",
            font=("Segoe UI", 16, "bold"),
            fg=p["text_primary"],
            bg=bg
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Manage local user profiles, visual theme preferences, demonstration datasets, and data backups",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=bg
        ).pack(anchor="w", pady=(2, 0))

        # Main Layout: 2 Columns
        cols_frame = tk.Frame(self.content, bg=bg, padx=pad_x, pady=0)
        cols_frame.pack(fill="both", expand=True)
        cols_frame.columnconfigure(0, weight=1)
        cols_frame.columnconfigure(1, weight=1)

        # Left Column: Profiles & Visual Theme
        left_box = tk.Frame(cols_frame, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left_box, text="ACTIVE PROFILE & DEMO DATA", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=surface).pack(anchor="w", pady=(0, 10))

        tk.Label(left_box, text="Active Profile:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.cmb_profiles = ttk.Combobox(left_box, state="readonly")
        self.cmb_profiles.pack(fill="x", pady=(2, 8))
        self.cmb_profiles.bind("<<ComboboxSelected>>", self._on_select_profile)

        # Seed Demo Data Button
        ttk.Button(
            left_box,
            text="Load Demo Profile (Alex Morgan — 60 Days)",
            style="Accent.TButton",
            command=self._seed_demo
        ).pack(fill="x", pady=(4, 14))

        tk.Frame(left_box, bg=border, height=1).pack(fill="x", pady=(0, 12))

        # Theme Section
        tk.Label(left_box, text="VISUAL APPEARANCE", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=surface).pack(anchor="w", pady=(0, 8))

        th_f = tk.Frame(left_box, bg=surface)
        th_f.pack(fill="x", pady=4)

        ttk.Button(th_f, text="Dark Theme", style="Secondary.TButton", command=lambda: self.on_theme_changed("dark")).pack(side="left", padx=(0, 6))
        ttk.Button(th_f, text="Light Theme", style="Secondary.TButton", command=lambda: self.on_theme_changed("light")).pack(side="left")

        # Right Column: Data Portability & Backup
        right_box = tk.Frame(cols_frame, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        right_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(right_box, text="LOCAL DATA SOVEREIGNTY & EXPORT", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=surface).pack(anchor="w", pady=(0, 10))

        tk.Label(
            right_box,
            text="DayBalance operates 100% offline. All records are stored in a local SQLite database with zero telemetry sent outside your machine.",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=surface,
            wraplength=380,
            justify="left"
        ).pack(anchor="w", pady=(0, 12))

        ttk.Button(right_box, text="Export Habit & Lifestyle CSV", style="Secondary.TButton", command=self._export_csv).pack(fill="x", pady=4)
        ttk.Button(right_box, text="Create JSON Full Database Backup", style="Secondary.TButton", command=self._export_json).pack(fill="x", pady=4)
        ttk.Button(right_box, text="Restore Database from JSON Backup", style="Secondary.TButton", command=self._restore_json).pack(fill="x", pady=4)

    def refresh(self):
        profiles = get_profiles()
        p_names = [f"{p['id']}: {p['name']}" for p in profiles]
        self.cmb_profiles["values"] = p_names

        cur_id = self.profile.get("id", 1)
        for idx, p in enumerate(profiles):
            if p["id"] == cur_id:
                self.cmb_profiles.current(idx)
                break

    def _on_select_profile(self, event=None):
        sel = self.cmb_profiles.get()
        if not sel:
            return
        p_id = int(sel.split(":")[0])
        profiles = get_profiles()
        for p in profiles:
            if p["id"] == p_id:
                self.profile = p
                self.on_profile_switched(p)
                break

    def _seed_demo(self):
        seed_demo_profile(force_refresh=True)
        messagebox.showinfo("Demo Data Loaded", "Alex Morgan demo dataset (60 days of correlated habits & health metrics) successfully loaded!")
        self.refresh()
        self.on_navigate("dashboard")

    def _export_csv(self):
        p_id = self.profile.get("id", 1)
        csv_str = export_entries_csv(p_id)
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(csv_str)
            messagebox.showinfo("Export Successful", f"Data exported successfully to:\n{path}")

    def _export_json(self):
        p_id = self.profile.get("id", 1)
        backup_str = export_profile_json(p_id)
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(backup_str)
            messagebox.showinfo("Backup Created", f"JSON backup successfully saved to:\n{path}")

    def _restore_json(self):
        p_id = self.profile.get("id", 1)
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                data_str = f.read()
            res = restore_profile_json(p_id, data_str)
            if res.get("status") == "success":
                messagebox.showinfo("Restore Successful", "Profile data restored successfully!")
                self.refresh()
                self.on_navigate("dashboard")
            else:
                err_msg = res.get("error", "Unknown error")
                messagebox.showerror("Restore Error", f"Failed to restore backup: {err_msg}")
