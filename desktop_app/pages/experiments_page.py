"""
DayBalance Desktop — Goals & Experiments Page
Manage A/B lifestyle experiments, baseline vs intervention evaluations, and quantitative habit goals.
"""

from datetime import date, timedelta
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any

from database.repository import create_experiment, get_experiments
from desktop_app.components import ScrollableFrame


class ExperimentsPage(tk.Frame):
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
            text="Goals & Empirical Experiments",
            font=("Segoe UI", 16, "bold"),
            fg=p["text_primary"],
            bg=bg
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Conduct personal before-and-after A/B interventions with baseline vs intervention delta evaluations",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=bg
        ).pack(anchor="w", pady=(2, 0))

        # Top Form: Design New Experiment
        form_box = tk.Frame(self.content, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        form_box.pack(fill="x", padx=pad_x, pady=(0, 18))

        tk.Label(form_box, text="DESIGN NEW LIFESTYLE EXPERIMENT", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=surface).pack(anchor="w", pady=(0, 10))

        fg = tk.Frame(form_box, bg=surface)
        fg.pack(fill="x")
        fg.columnconfigure((0, 1), weight=1)

        # Hypothesis
        tk.Label(fg, text="Hypothesis / Goal:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).grid(row=0, column=0, sticky="w", padx=4)
        self.ent_hypo = ttk.Entry(fg)
        self.ent_hypo.insert(0, "Does 8+ hours sleep increase morning study focus by 20%?")
        self.ent_hypo.grid(row=1, column=0, columnspan=2, sticky="ew", padx=4, pady=(2, 8))

        # Metric
        tk.Label(fg, text="Primary Metric:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).grid(row=2, column=0, sticky="w", padx=4)
        self.cmb_metric = ttk.Combobox(fg, values=["study_minutes", "completion_rate", "energy_score", "mood_score"], state="readonly")
        self.cmb_metric.set("study_minutes")
        self.cmb_metric.grid(row=3, column=0, sticky="ew", padx=4, pady=(2, 8))

        # Expected Direction
        tk.Label(fg, text="Expected Direction:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).grid(row=2, column=1, sticky="w", padx=4)
        self.cmb_dir = ttk.Combobox(fg, values=["increase", "decrease"], state="readonly")
        self.cmb_dir.set("increase")
        self.cmb_dir.grid(row=3, column=1, sticky="ew", padx=4, pady=(2, 8))

        # Dates Grid
        today = date.today()
        b_start = (today - timedelta(days=14)).isoformat()
        b_end = (today - timedelta(days=7)).isoformat()
        i_start = (today - timedelta(days=6)).isoformat()
        i_end = today.isoformat()

        dates_f = tk.Frame(form_box, bg=surface)
        dates_f.pack(fill="x", pady=4)
        dates_f.columnconfigure((0, 1, 2, 3), weight=1)

        tk.Label(dates_f, text="Baseline Start:", font=("Segoe UI", 8), fg=p["text_secondary"], bg=surface).grid(row=0, column=0, sticky="w")
        self.ent_b_s = ttk.Entry(dates_f)
        self.ent_b_s.insert(0, b_start)
        self.ent_b_s.grid(row=1, column=0, sticky="ew", padx=2)

        tk.Label(dates_f, text="Baseline End:", font=("Segoe UI", 8), fg=p["text_secondary"], bg=surface).grid(row=0, column=1, sticky="w")
        self.ent_b_e = ttk.Entry(dates_f)
        self.ent_b_e.insert(0, b_end)
        self.ent_b_e.grid(row=1, column=1, sticky="ew", padx=2)

        tk.Label(dates_f, text="Intervention Start:", font=("Segoe UI", 8), fg=p["text_secondary"], bg=surface).grid(row=0, column=2, sticky="w")
        self.ent_i_s = ttk.Entry(dates_f)
        self.ent_i_s.insert(0, i_start)
        self.ent_i_s.grid(row=1, column=2, sticky="ew", padx=2)

        tk.Label(dates_f, text="Intervention End:", font=("Segoe UI", 8), fg=p["text_secondary"], bg=surface).grid(row=0, column=3, sticky="w")
        self.ent_i_e = ttk.Entry(dates_f)
        self.ent_i_e.insert(0, i_end)
        self.ent_i_e.grid(row=1, column=3, sticky="ew", padx=2)

        ttk.Button(form_box, text="Launch Experiment", style="Accent.TButton", command=self._create_experiment).pack(anchor="e", pady=(10, 0))

        # Active Experiments List
        list_box = tk.Frame(self.content, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        list_box.pack(fill="both", expand=True, padx=pad_x, pady=(0, 24))

        tk.Label(list_box, text="ACTIVE & HISTORICAL EXPERIMENTS", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=surface).pack(anchor="w", pady=(0, 10))

        self.exp_list_frame = tk.Frame(list_box, bg=surface)
        self.exp_list_frame.pack(fill="both", expand=True)

    def refresh(self):
        p_id = self.profile.get("id", 1)
        experiments = get_experiments(p_id)

        for w in self.exp_list_frame.winfo_children():
            w.destroy()

        if not experiments:
            tk.Label(self.exp_list_frame, text="No experiments launched yet. Launch an experiment above to track behavior deltas.", font=("Segoe UI", 9), fg=self.p["text_muted"], bg=self.p["surface"], pady=16).pack()
            return

        for exp in experiments:
            row = tk.Frame(self.exp_list_frame, bg=self.p["bg"], highlightbackground=self.p["border"], highlightthickness=1, padx=14, pady=10)
            row.pack(fill="x", pady=4)

            title = exp.get("title") or exp.get("hypothesis", "Experiment")
            hypo = exp.get("hypothesis", "")
            metric = exp.get("primary_metric", "study_minutes")
            status = exp.get("status", "active")
            tk.Label(row, text=title, font=("Segoe UI", 9, "bold"), fg=self.p["text_primary"], bg=self.p["bg"]).pack(anchor="w")
            sub = f"Hypothesis: {hypo} • Metric: {metric} • Status: {status.capitalize()}"
            tk.Label(row, text=sub, font=("Segoe UI", 8), fg=self.p["text_secondary"], bg=self.p["bg"]).pack(anchor="w", pady=(2, 0))

    def _create_experiment(self):
        hypo = self.ent_hypo.get().strip()
        if not hypo:
            messagebox.showwarning("Validation Error", "Hypothesis cannot be empty.")
            return

        metric = self.cmb_metric.get()
        b_s = self.ent_b_s.get().strip()
        b_e = self.ent_b_e.get().strip()
        i_s = self.ent_i_s.get().strip()
        i_e = self.ent_i_e.get().strip()

        p_id = self.profile.get("id", 1)
        title = hypo[:50] + ("..." if len(hypo) > 50 else "")
        create_experiment(
            profile_id=p_id,
            title=title,
            hypothesis=hypo,
            primary_metric=metric,
            baseline_start=b_s,
            baseline_end=b_e,
            intervention_start=i_s,
            intervention_end=i_e
        )
        self.refresh()
        messagebox.showinfo("Success", "Experiment successfully launched!")
