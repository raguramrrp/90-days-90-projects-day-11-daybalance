"""
DayBalance Desktop UI Theme System
Implements Sage Green, Warm Ivory & Editorial Wellness palettes for Tkinter & ttk.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

PALETTES: Dict[str, Dict[str, str]] = {
    "dark": {
        "bg": "#0D0E12",
        "surface": "#171B24",
        "surface_hover": "#202633",
        "surface_card": "#171B24",
        "border": "#26354A",
        "border_subtle": "#1B2330",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
        "text_muted": "#64748B",
        "accent": "#10B981",
        "accent_hover": "#059669",
        "accent_bg": "#064E3B",
        "accent_text": "#FFFFFF",
        "pill_container_bg": "#161D27",
        "pill_container_border": "#26354A",
        "pill_bg": "#161D27",
        "pill_border": "#26354A",
        "pill_active_bg": "#10B981",
        "pill_active_fg": "#FFFFFF",
        "pill_inactive_fg": "#CBD5E1",
        "pill_hover_bg": "#202633",
        "success": "#10B981",
        "success_bg": "#064E3B",
        "warning": "#F59E0B",
        "warning_bg": "#78350F",
        "danger": "#EF4444",
        "danger_bg": "#7F1D1D",
        "info": "#3B82F6",
        "info_bg": "#1E3A8A",
        "input_bg": "#0D0E12",
        "input_fg": "#F8FAFC",
        "tree_select_bg": "#065F46",
        "tree_select_fg": "#FFFFFF",
    },
    "light": {
        "bg": "#F8FAFC",
        "surface": "#FFFFFF",
        "surface_hover": "#F1F5F9",
        "surface_card": "#FFFFFF",
        "border": "#E2E8F0",
        "border_subtle": "#F1F5F9",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#64748B",
        "accent": "#059669",
        "accent_hover": "#047857",
        "accent_bg": "#DEF7EC",
        "accent_text": "#FFFFFF",
        "pill_container_bg": "#F1F5F9",
        "pill_container_border": "#E2E8F0",
        "pill_bg": "#F1F5F9",
        "pill_border": "#CBD5E1",
        "pill_active_bg": "#059669",
        "pill_active_fg": "#FFFFFF",
        "pill_inactive_fg": "#1E293B",
        "pill_hover_bg": "#E2E8F0",
        "success": "#059669",
        "success_bg": "#DEF7EC",
        "warning": "#D97706",
        "warning_bg": "#FEF3C7",
        "danger": "#DC2626",
        "danger_bg": "#FEE2E2",
        "info": "#2563EB",
        "info_bg": "#DBEAFE",
        "input_bg": "#FFFFFF",
        "input_fg": "#0F172A",
        "tree_select_bg": "#DEF7EC",
        "tree_select_fg": "#065F46",
    }
}


def apply_theme(root: tk.Tk, theme_name: str = "dark") -> Dict[str, str]:
    """Applies theme colors to Tkinter root and configures ttk widget styles."""
    p = PALETTES.get(theme_name, PALETTES["dark"])
    root.configure(bg=p["bg"])

    style = ttk.Style(root)
    # Use clam as base engine for reliable color overrides across Windows
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Standard ttk Button styles
    style.configure(
        "TButton",
        background=p["surface"],
        foreground=p["text_primary"],
        bordercolor=p["border"],
        darkcolor=p["surface"],
        lightcolor=p["surface"],
        focuscolor=p["accent"],
        font=("Segoe UI", 9, "bold"),
        padding=(12, 6)
    )
    style.map(
        "TButton",
        background=[("active", p["surface_hover"]), ("pressed", p["accent_bg"])],
        foreground=[("active", p["text_primary"])]
    )

    style.configure(
        "Accent.TButton",
        background=p["accent"],
        foreground="#FFFFFF",
        bordercolor=p["accent_hover"],
        darkcolor=p["accent"],
        lightcolor=p["accent"],
        focuscolor=p["accent_hover"],
        font=("Segoe UI", 9, "bold"),
        padding=(14, 6)
    )
    style.map(
        "Accent.TButton",
        background=[("active", p["accent_hover"]), ("pressed", p["accent_hover"])],
        foreground=[("active", "#FFFFFF")]
    )

    style.configure(
        "Secondary.TButton",
        background=p["bg"],
        foreground=p["text_secondary"],
        bordercolor=p["border"],
        font=("Segoe UI", 9),
        padding=(10, 5)
    )
    style.map(
        "Secondary.TButton",
        background=[("active", p["surface_hover"])],
        foreground=[("active", p["text_primary"])]
    )

    # Entry styles
    style.configure(
        "TEntry",
        fieldbackground=p["input_bg"],
        foreground=p["input_fg"],
        bordercolor=p["border"],
        darkcolor=p["input_bg"],
        lightcolor=p["input_bg"],
        padding=6
    )

    # Treeview styles (Tables)
    style.configure(
        "Treeview",
        background=p["surface"],
        foreground=p["text_primary"],
        fieldbackground=p["surface"],
        bordercolor=p["border"],
        font=("Segoe UI", 9),
        rowheight=32
    )
    style.map(
        "Treeview",
        background=[("selected", p["tree_select_bg"])],
        foreground=[("selected", p["tree_select_fg"])]
    )
    style.configure(
        "Treeview.Heading",
        background=p["bg"],
        foreground=p["text_secondary"],
        bordercolor=p["border"],
        font=("Segoe UI", 8, "bold"),
        padding=6
    )

    # Scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=p["surface"],
        bordercolor=p["border"],
        troughcolor=p["bg"],
        arrowcolor=p["text_secondary"]
    )

    return p
