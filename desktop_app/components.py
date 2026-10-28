"""
DayBalance Desktop UI Custom Components
Bento Stat Cards, Live Health Cards, Rounded Bento Containers, Curvy Controls & Telemetry.
"""

import math
import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List, Callable


class CurvyButton(tk.Canvas):
    """
    Smooth, anti-aliased curved pill button drawn with Tkinter Canvas.
    Replaces boxy rectangular default buttons with sleek, modern curvy pill buttons.
    """
    def __init__(
        self,
        parent,
        text: str,
        command: Optional[Callable[[], None]] = None,
        bg_color: str = "#10B981",
        hover_color: str = "#059669",
        fg_color: str = "#FFFFFF",
        border_color: Optional[str] = None,
        radius: int = 14,
        width: int = 110,
        height: int = 32,
        font: tuple = ("Segoe UI", 9, "bold"),
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent.cget("bg"),
            highlightthickness=0,
            borderwidth=0,
            cursor="hand2",
            **kwargs
        )
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.border_color = border_color or bg_color
        self.radius = radius
        self.w = width
        self.h = height
        self.font = font
        self.is_hovered = False

        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw(self):
        self.delete("all")
        color = self.hover_color if self.is_hovered else self.bg_color
        b_color = self.border_color
        r = self.radius
        w = self.w
        h = self.h
        pad = 2
        points = [
            pad + r, pad,
            w - pad - r, pad,
            w - pad, pad,
            w - pad, pad + r,
            w - pad, h - pad - r,
            w - pad, h - pad,
            w - pad - r, h - pad,
            pad + r, h - pad,
            pad, h - pad,
            pad, h - pad - r,
            pad, pad + r,
            pad, pad
        ]
        self.create_polygon(points, smooth=True, fill=color, outline=b_color, width=1)
        self.create_text(w // 2, h // 2, text=self.text, fill=self.fg_color, font=self.font)

    def _on_enter(self, event=None):
        self.is_hovered = True
        self._draw()

    def _on_leave(self, event=None):
        self.is_hovered = False
        self._draw()

    def _on_click(self, event=None):
        if self.command:
            self.command()

    def set_text(self, text: str):
        self.text = text
        self._draw()

    def configure_colors(self, bg_color: str, hover_color: str, fg_color: str, border_color: Optional[str] = None):
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.border_color = border_color or bg_color
        self._draw()


class CurvyCheck(tk.Canvas):
    """
    Curved squircle checkmark box drawn with Tkinter Canvas.
    Renders a smooth green rounded box with white checkmark when completed,
    or an outlined squircle when pending.
    """
    def __init__(
        self,
        parent,
        is_completed: bool = False,
        command: Optional[Callable[[], None]] = None,
        palette: Dict[str, str] = None,
        size: int = 22,
        **kwargs
    ):
        p = palette or {}
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=parent.cget("bg"),
            highlightthickness=0,
            borderwidth=0,
            cursor="hand2",
            **kwargs
        )
        self.is_completed = is_completed
        self.command = command
        self.palette = p
        self.size = size

        self._draw()
        self.bind("<Button-1>", self._on_click)

    def _draw(self):
        self.delete("all")
        p = self.palette
        s = self.size
        pad = 2
        r = 6

        accent = p.get("accent", "#10B981")
        border = p.get("border", "#26354A")
        bg_col = accent if self.is_completed else p.get("surface", "#171B24")
        out_col = accent if self.is_completed else border

        points = [
            pad + r, pad,
            s - pad - r, pad,
            s - pad, pad,
            s - pad, pad + r,
            s - pad, s - pad - r,
            s - pad, s - pad,
            s - pad - r, s - pad,
            pad + r, s - pad,
            pad, s - pad,
            pad, s - pad - r,
            pad, pad + r,
            pad, pad
        ]
        self.create_polygon(points, smooth=True, fill=bg_col, outline=out_col, width=1.5)
        if self.is_completed:
            self.create_text(s // 2, s // 2, text="✓", fill="#FFFFFF", font=("Segoe UI", 9, "bold"))

    def _on_click(self, event=None):
        if self.command:
            self.command()

    def set_completed(self, is_completed: bool):
        self.is_completed = is_completed
        self._draw()


class ProfileLogo(tk.Canvas):
    """
    Universal vector avatar icon drawn on Canvas with smooth circle and user silhouette.
    Replaces raw text badges (e.g. 'AM') with a clean, modern profile silhouette logo.
    """
    def __init__(self, parent, size: int = 28, palette: Dict[str, str] = None, **kwargs):
        p = palette or {}
        bg = parent.cget("bg")
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0, borderwidth=0, **kwargs)
        self.size = size
        self.palette = p
        self._draw()

    def _draw(self):
        self.delete("all")
        s = self.size
        cx, cy = s // 2, s // 2
        r_outer = (s - 2) // 2

        p = self.palette
        avatar_bg = p.get("accent_bg", "#064E3B")
        avatar_fg = p.get("accent", "#10B981")

        # Outer circle background with subtle ring
        self.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer, fill=avatar_bg, outline=avatar_fg, width=1)

        # Vector head silhouette
        r_head = s * 0.16
        head_y = cy - s * 0.12
        self.create_oval(cx - r_head, head_y - r_head, cx + r_head, head_y + r_head, fill=avatar_fg, outline="")

        # Vector torso / shoulders arc silhouette
        body_w = s * 0.52
        body_h = s * 0.38
        body_y = cy + s * 0.22
        self.create_arc(
            cx - body_w / 2, body_y - body_h / 2,
            cx + body_w / 2, body_y + body_h / 2,
            start=0, extent=180, fill=avatar_fg, outline=""
        )


class ThemeToggleButton(tk.Canvas):
    """
    Curved pill theme toggle button featuring smooth vector Sun (amber circle + 8 rays) in dark mode
    and Moon (deep crescent) in light mode. Strictly vector canvas rendering with zero emojis.
    """
    def __init__(
        self,
        parent,
        is_dark: bool = True,
        command: Optional[Callable[[], None]] = None,
        palette: Dict[str, str] = None,
        width: int = 44,
        height: int = 28,
        radius: int = 14,
        **kwargs
    ):
        p = palette or {}
        bg = parent.cget("bg")
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg,
            highlightthickness=0,
            borderwidth=0,
            cursor="hand2",
            **kwargs
        )
        self.is_dark = is_dark
        self.command = command
        self.palette = p
        self.w = width
        self.h = height
        self.radius = radius
        self.is_hovered = False

        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw(self):
        self.delete("all")
        w, h, r = self.w, self.h, self.radius
        pad = 2

        if self.is_dark:
            btn_bg = "#202633" if not self.is_hovered else "#2C3545"
            border = "#26354A"
        else:
            btn_bg = "#F1F5F9" if not self.is_hovered else "#E2E8F0"
            border = "#CBD5E1"

        points = [
            pad + r, pad,
            w - pad - r, pad,
            w - pad, pad,
            w - pad, pad + r,
            w - pad, h - pad - r,
            w - pad, h - pad,
            w - pad - r, h - pad,
            pad + r, h - pad,
            pad, h - pad,
            pad, h - pad - r,
            pad, pad + r,
            pad, pad
        ]
        self.create_polygon(points, smooth=True, fill=btn_bg, outline=border, width=1)

        cx, cy = w // 2, h // 2
        if self.is_dark:
            # Sun icon (amber circle + 8 rays)
            sun_color = "#F59E0B"
            r_sun = 4.5
            self.create_oval(cx - r_sun, cy - r_sun, cx + r_sun, cy + r_sun, fill=sun_color, outline=sun_color)
            d1, d2 = 6.5, 9.5
            for i in range(8):
                angle = i * (math.pi / 4)
                x1 = cx + d1 * math.cos(angle)
                y1 = cy + d1 * math.sin(angle)
                x2 = cx + d2 * math.cos(angle)
                y2 = cy + d2 * math.sin(angle)
                self.create_line(x1, y1, x2, y2, fill=sun_color, width=1.5, capstyle="round")
        else:
            # Crescent Moon icon
            moon_color = "#334155"
            r_moon = 6.0
            self.create_oval(cx - r_moon, cy - r_moon, cx + r_moon, cy + r_moon, fill=moon_color, outline=moon_color)
            c_off_x, c_off_y = 2.5, -2.0
            r_cut = 5.2
            self.create_oval(cx - r_cut + c_off_x, cy - r_cut + c_off_y, cx + r_cut + c_off_x, cy + r_cut + c_off_y, fill=btn_bg, outline=btn_bg)

    def _on_enter(self, event=None):
        self.is_hovered = True
        self._draw()

    def _on_leave(self, event=None):
        self.is_hovered = False
        self._draw()

    def _on_click(self, event=None):
        if self.command:
            self.command()


class RoundedCard(tk.Canvas):
    """
    Smooth, anti-aliased rounded container card drawn with Tkinter Canvas.
    Replaces sharp rectangular boxes with elegant rounded corners (radius 14-16px).
    Embeds an inner frame where child widgets can be packed or gridded cleanly.
    """
    def __init__(
        self,
        parent,
        bg_color: str = "#171B24",
        border_color: str = "#26354A",
        parent_bg: str = "#0D0E12",
        radius: int = 16,
        inset: int = 14,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=parent_bg,
            highlightthickness=0,
            borderwidth=0,
            **kwargs
        )
        self.bg_color = bg_color
        self.border_color = border_color
        self.parent_bg = parent_bg
        self.radius = radius
        self.inset = inset

        self.inner = tk.Frame(self, bg=bg_color)
        self.win_id = self.create_window(inset + 2, inset + 2, window=self.inner, anchor="nw")
        self.bind("<Configure>", self._on_canvas_resize)

    def _on_canvas_resize(self, event):
        w, h = event.width, event.height
        if w < 10 or h < 10:
            return
        self.delete("bg_poly")
        r = self.radius
        pad = 2
        points = [
            pad + r, pad,
            w - pad - r, pad,
            w - pad, pad,
            w - pad, pad + r,
            w - pad, h - pad - r,
            w - pad, h - pad,
            w - pad - r, h - pad,
            pad + r, h - pad,
            pad, h - pad,
            pad, h - pad - r,
            pad, pad + r,
            pad, pad
        ]
        self.create_polygon(points, smooth=True, fill=self.bg_color, outline=self.border_color, width=1, tags="bg_poly")
        self.tag_lower("bg_poly")
        self.coords(self.win_id, pad + self.inset, pad + self.inset)
        self.itemconfig(self.win_id, width=max(1, w - 2 * (pad + self.inset)), height=max(1, h - 2 * (pad + self.inset)))

    def configure_colors(self, bg_color: str, border_color: str, parent_bg: Optional[str] = None):
        self.bg_color = bg_color
        self.border_color = border_color
        if parent_bg:
            self.parent_bg = parent_bg
            self.config(bg=parent_bg)
        self.inner.config(bg=bg_color)
        w = self.winfo_width()
        h = self.winfo_height()
        if w > 10 and h > 10:
            class DummyEvent:
                width = w
                height = h
            self._on_canvas_resize(DummyEvent())


class RoundedPillFrame(tk.Canvas):
    """
    Smooth, anti-aliased pill-shaped container drawn with Tkinter Canvas.
    Automatically resizes its width and height to comfortably wrap inner widgets.
    """
    def __init__(
        self,
        parent,
        bg_color: str = "#161D27",
        border_color: str = "#26354A",
        parent_bg: str = "#0D0E12",
        radius: int = 16,
        padx: int = 8,
        pady: int = 3,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=parent_bg,
            highlightthickness=0,
            borderwidth=0,
            **kwargs
        )
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        self.padx = padx
        self.pady = pady

        self.inner = tk.Frame(self, bg=bg_color)
        self.win_id = self.create_window(padx, pady, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", self._on_inner_config)

    def _on_inner_config(self, event=None):
        req_w = self.inner.winfo_reqwidth()
        req_h = self.inner.winfo_reqheight()
        w = req_w + 2 * self.padx
        h = req_h + 2 * self.pady
        self.config(width=w, height=h)
        self._redraw(w, h)

    def _redraw(self, w: int, h: int):
        self.delete("pill_bg")
        r = self.radius
        pad = 1
        points = [
            pad + r, pad,
            w - pad - r, pad,
            w - pad, pad,
            w - pad, pad + r,
            w - pad, h - pad - r,
            w - pad, h - pad,
            w - pad - r, h - pad,
            pad + r, h - pad,
            pad, h - pad,
            pad, h - pad - r,
            pad, pad + r,
            pad, pad
        ]
        self.create_polygon(points, smooth=True, fill=self.bg_color, outline=self.border_color, width=1, tags="pill_bg")
        self.tag_lower("pill_bg")
        self.coords(self.win_id, self.padx, self.pady)

    def configure_colors(self, bg_color: str, border_color: str, parent_bg: Optional[str] = None):
        self.bg_color = bg_color
        self.border_color = border_color
        if parent_bg:
            self.config(bg=parent_bg)
        self.inner.config(bg=bg_color)
        self._on_inner_config()


class StatCard(tk.Frame):
    """Modern Bento Stat Card with label, big numeric value, and context subtext."""

    def __init__(
        self,
        parent,
        label: str,
        value: str,
        subtext: str,
        palette: Dict[str, str],
        accent_color: Optional[str] = None,
        **kwargs
    ):
        p = palette
        bg = p.get("surface", "#1E293B")
        border = p.get("border", "#334155")
        text_pri = p.get("text_primary", "#F8FAFC")
        text_sec = p.get("text_secondary", "#94A3B8")
        accent = accent_color or p.get("accent", "#10B981")

        super().__init__(
            parent,
            bg=bg,
            highlightbackground=border,
            highlightthickness=1,
            padx=16,
            pady=14,
            **kwargs
        )
        self.p = p

        # Label Row
        self.lbl_title = tk.Label(
            self,
            text=label.upper(),
            font=("Segoe UI", 8, "bold"),
            fg=text_sec,
            bg=bg,
            anchor="w"
        )
        self.lbl_title.pack(fill="x")

        # Main Value
        self.lbl_val = tk.Label(
            self,
            text=value,
            font=("Segoe UI", 18, "bold"),
            fg=text_pri,
            bg=bg,
            anchor="w"
        )
        self.lbl_val.pack(fill="x", pady=(4, 2))

        # Thin Accent Line
        self.bar = tk.Frame(self, bg=accent, height=3)
        self.bar.pack(fill="x", pady=(2, 6))

        # Subtext
        self.lbl_sub = tk.Label(
            self,
            text=subtext,
            font=("Segoe UI", 8),
            fg=text_sec,
            bg=bg,
            anchor="w"
        )
        self.lbl_sub.pack(fill="x")

    def update_data(self, value: str, subtext: str):
        self.lbl_val.config(text=value)
        self.lbl_sub.config(text=subtext)


class HealthCard(tk.Frame):
    """Biometric Health & Wearable Card with Status Badge and Visual Progress Meter."""

    def __init__(
        self,
        parent,
        label: str,
        value: str,
        subtext: str,
        status_badge: str,
        progress_pct: float,
        palette: Dict[str, str],
        bar_color: Optional[str] = None,
        **kwargs
    ):
        p = palette
        bg = p.get("surface", "#1E293B")
        border = p.get("border", "#334155")
        text_pri = p.get("text_primary", "#F8FAFC")
        text_sec = p.get("text_secondary", "#94A3B8")
        bar_c = bar_color or p.get("accent", "#10B981")

        super().__init__(
            parent,
            bg=bg,
            highlightbackground=border,
            highlightthickness=1,
            padx=16,
            pady=14,
            **kwargs
        )

        # Header Row: Label & Status Pill
        hdr = tk.Frame(self, bg=bg)
        hdr.pack(fill="x")

        tk.Label(
            hdr,
            text=label.upper(),
            font=("Segoe UI", 8, "bold"),
            fg=text_sec,
            bg=bg,
            anchor="w"
        ).pack(side="left")

        badge_bg = p.get("accent_bg", "#064E3B")
        badge_fg = p.get("accent", "#10B981")
        self.badge_lbl = tk.Label(
            hdr,
            text=status_badge,
            font=("Segoe UI", 7, "bold"),
            fg=badge_fg,
            bg=badge_bg,
            padx=6,
            pady=2
        )
        self.badge_lbl.pack(side="right")

        # Value
        self.lbl_val = tk.Label(
            self,
            text=value,
            font=("Segoe UI", 16, "bold"),
            fg=text_pri,
            bg=bg,
            anchor="w"
        )
        self.lbl_val.pack(fill="x", pady=(6, 4))

        # Progress Meter Container
        meter_bg = p.get("bg", "#0F172A")
        self.meter_track = tk.Frame(self, bg=meter_bg, height=6)
        self.meter_track.pack(fill="x", pady=(2, 6))

        clamped_pct = max(0.0, min(1.0, progress_pct))
        self.meter_fill = tk.Frame(self.meter_track, bg=bar_c, height=6)
        self.meter_fill.place(relx=0, rely=0, relwidth=clamped_pct, relheight=1.0)

        # Subtext
        self.lbl_sub = tk.Label(
            self,
            text=subtext,
            font=("Segoe UI", 8),
            fg=text_sec,
            bg=bg,
            anchor="w"
        )
        self.lbl_sub.pack(fill="x")

    def update_data(self, value: str, subtext: str, status_badge: str, progress_pct: float):
        self.lbl_val.config(text=value)
        self.lbl_sub.config(text=subtext)
        self.badge_lbl.config(text=status_badge)
        clamped_pct = max(0.0, min(1.0, progress_pct))
        self.meter_fill.place(relx=0, rely=0, relwidth=clamped_pct, relheight=1.0)


class ScrollableFrame(tk.Frame):
    """A high-performance scrollable canvas frame that responds to mousewheel."""

    def __init__(self, parent, bg: str, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_content = tk.Frame(self.canvas, bg=bg)

        self.content_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_content,
            anchor="nw"
        )

        self.scrollable_content.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mousewheel binding
        self.bind_mousewheel(self)
        self.bind_mousewheel(self.canvas)
        self.bind_mousewheel(self.scrollable_content)

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.content_window, width=event.width)

    def bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel, add="+")

    def _on_mousewheel(self, event):
        # On Windows event.delta is typically +/- 120
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class StreakBentoCard(RoundedCard):
    """Bento Card displaying prominent streak flame, giant streak number, and best streak with smooth rounded corners."""

    def __init__(
        self,
        parent,
        streak_days: int = 44,
        best_streak: int = 52,
        palette: Dict[str, str] = None,
        **kwargs
    ):
        p = palette or {}
        bg = p.get("surface", "#171B24")
        border = p.get("border", "#26354A")
        parent_bg = p.get("bg", "#0D0E12")
        text_pri = p.get("text_primary", "#F8FAFC")
        text_sec = p.get("text_secondary", "#94A3B8")
        warning = p.get("warning", "#F59E0B")

        super().__init__(
            parent,
            bg_color=bg,
            border_color=border,
            parent_bg=parent_bg,
            radius=16,
            inset=14,
            **kwargs
        )
        self.p = p

        tk.Label(
            self.inner,
            text="CURRENT STREAK",
            font=("Segoe UI", 8, "bold"),
            fg=text_sec,
            bg=bg,
            anchor="w"
        ).pack(fill="x")

        mid_frame = tk.Frame(self.inner, bg=bg)
        mid_frame.pack(fill="x", pady=(10, 4))

        tk.Label(
            mid_frame,
            text="🔥",
            font=("Segoe UI", 26),
            fg=warning,
            bg=bg
        ).pack(side="left", padx=(0, 8))

        val_box = tk.Frame(mid_frame, bg=bg)
        val_box.pack(side="left")

        self.lbl_streak_val = tk.Label(
            val_box,
            text=str(streak_days),
            font=("Segoe UI", 26, "bold"),
            fg=text_pri,
            bg=bg,
            anchor="w"
        )
        self.lbl_streak_val.pack(anchor="w")

        tk.Label(
            val_box,
            text="day streak",
            font=("Segoe UI", 9),
            fg=text_sec,
            bg=bg,
            anchor="w"
        ).pack(anchor="w", pady=(0, 2))

        self.lbl_best = tk.Label(
            self.inner,
            text=f"Historical best: {best_streak} days",
            font=("Segoe UI", 8),
            fg=text_sec,
            bg=bg,
            anchor="w"
        )
        self.lbl_best.pack(fill="x", pady=(8, 0))

    def update_data(self, streak_days: int, best_streak: int):
        self.lbl_streak_val.config(text=str(streak_days))
        self.lbl_best.config(text=f"Historical best: {best_streak} days")


class ConsistencyBentoCard(RoundedCard):
    """Bento Card displaying prominent 30-Day Consistency percentage and glowing progress bar with smooth rounded corners."""

    def __init__(
        self,
        parent,
        consistency_pct: float = 87.4,
        subtext: str = "Scheduled habit completion",
        palette: Dict[str, str] = None,
        **kwargs
    ):
        p = palette or {}
        bg = p.get("surface", "#171B24")
        border = p.get("border", "#26354A")
        parent_bg = p.get("bg", "#0D0E12")
        text_pri = p.get("text_primary", "#F8FAFC")
        text_sec = p.get("text_secondary", "#94A3B8")
        accent = p.get("accent", "#10B981")

        super().__init__(
            parent,
            bg_color=bg,
            border_color=border,
            parent_bg=parent_bg,
            radius=16,
            inset=14,
            **kwargs
        )
        self.p = p

        tk.Label(
            self.inner,
            text="30-DAY CONSISTENCY",
            font=("Segoe UI", 8, "bold"),
            fg=text_sec,
            bg=bg,
            anchor="w"
        ).pack(fill="x")

        self.lbl_pct = tk.Label(
            self.inner,
            text=f"{consistency_pct:.1f}%",
            font=("Segoe UI", 26, "bold"),
            fg=text_pri,
            bg=bg,
            anchor="w"
        )
        self.lbl_pct.pack(fill="x", pady=(8, 2))

        track_bg = p.get("border_subtle", "#1B2330")
        self.meter_track = tk.Frame(self.inner, bg=track_bg, height=8)
        self.meter_track.pack(fill="x", pady=(4, 8))

        clamped = max(0.0, min(1.0, consistency_pct / 100.0))
        self.meter_fill = tk.Frame(self.meter_track, bg=accent, height=8)
        self.meter_fill.place(relx=0, rely=0, relwidth=clamped, relheight=1.0)

        self.lbl_sub = tk.Label(
            self.inner,
            text=subtext,
            font=("Segoe UI", 8),
            fg=text_sec,
            bg=bg,
            anchor="w"
        )
        self.lbl_sub.pack(fill="x")

    def update_data(self, consistency_pct: float, subtext: str = "Scheduled habit completion"):
        self.lbl_pct.config(text=f"{consistency_pct:.1f}%")
        self.lbl_sub.config(text=subtext)
        clamped = max(0.0, min(1.0, consistency_pct / 100.0))
        self.meter_fill.place(relx=0, rely=0, relwidth=clamped, relheight=1.0)


class TargetProgressBentoCard(RoundedCard):
    """Bento Card displaying 4 glowing horizontal progress bars for daily targets with smooth rounded corners."""

    def __init__(
        self,
        parent,
        targets: Optional[List[Dict[str, Any]]] = None,
        palette: Dict[str, str] = None,
        **kwargs
    ):
        p = palette or {}
        bg = p.get("surface", "#171B24")
        border = p.get("border", "#26354A")
        parent_bg = p.get("bg", "#0D0E12")
        text_pri = p.get("text_primary", "#F8FAFC")
        text_sec = p.get("text_secondary", "#94A3B8")
        self.accent = p.get("accent", "#10B981")

        super().__init__(
            parent,
            bg_color=bg,
            border_color=border,
            parent_bg=parent_bg,
            radius=16,
            inset=14,
            **kwargs
        )
        self.p = p

        hdr = tk.Frame(self.inner, bg=bg)
        hdr.pack(fill="x")

        tk.Label(
            hdr,
            text="TARGET PROGRESS",
            font=("Segoe UI", 8, "bold"),
            fg=text_sec,
            bg=bg,
            anchor="w"
        ).pack(side="left")

        tk.Label(
            hdr,
            text="Today",
            font=("Segoe UI", 8),
            fg=self.accent,
            bg=bg
        ).pack(side="right")

        self.bars_container = tk.Frame(self.inner, bg=bg)
        self.bars_container.pack(fill="both", expand=True, pady=(8, 0))

        self.update_targets(targets or [])

    def update_targets(self, targets: List[Dict[str, Any]]):
        p = self.p
        bg = p.get("surface", "#171B24")
        text_pri = p.get("text_primary", "#F8FAFC")
        text_sec = p.get("text_secondary", "#94A3B8")
        track_bg = p.get("border_subtle", "#1B2330")

        for w in self.bars_container.winfo_children():
            w.destroy()

        if not targets:
            targets = [
                {"label": "Deep Work", "val_str": "2h 45m / 3h 00m", "pct": 0.91},
                {"label": "Water Intake", "val_str": "2,400 / 3,000 ml", "pct": 0.80},
                {"label": "Exercise", "val_str": "45 / 45 min", "pct": 1.00},
                {"label": "Sleep", "val_str": "7.8 / 8.0 hrs", "pct": 0.97},
            ]

        for item in targets:
            row = tk.Frame(self.bars_container, bg=bg)
            row.pack(fill="x", pady=2)

            info_row = tk.Frame(row, bg=bg)
            info_row.pack(fill="x")

            tk.Label(
                info_row,
                text=item["label"],
                font=("Segoe UI", 8, "bold"),
                fg=text_pri,
                bg=bg
            ).pack(side="left")

            pct_val = int(round(item["pct"] * 100))
            tk.Label(
                info_row,
                text=f"{item['val_str']} ({pct_val}%)",
                font=("Segoe UI", 8),
                fg=text_sec,
                bg=bg
            ).pack(side="right")

            track = tk.Frame(row, bg=track_bg, height=5)
            track.pack(fill="x", pady=(2, 2))

            clamped = max(0.0, min(1.0, item["pct"]))
            fill = tk.Frame(track, bg=self.accent, height=5)
            fill.place(relx=0, rely=0, relwidth=clamped, relheight=1.0)


class WearableBentoCard(RoundedCard):
    """Bento Card displaying Smart Health & Wearable telemetry with smooth rounded corners."""

    def __init__(
        self,
        parent,
        device_name: str = "Galaxy Watch6 Classic",
        battery: int = 84,
        is_connected: bool = True,
        vitals: Optional[Dict[str, Any]] = None,
        on_sync: Optional[Callable[[], None]] = None,
        on_manage: Optional[Callable[[], None]] = None,
        palette: Dict[str, str] = None,
        **kwargs
    ):
        p = palette or {}
        bg = p.get("surface", "#171B24")
        border = p.get("border", "#26354A")
        parent_bg = p.get("bg", "#0D0E12")

        super().__init__(
            parent,
            bg_color=bg,
            border_color=border,
            parent_bg=parent_bg,
            radius=16,
            inset=12,
            **kwargs
        )
        self.p = p
        self.on_sync = on_sync
        self.on_manage = on_manage

        banner_bg = p.get("accent_bg", "#064E3B")
        banner_fg = p.get("accent", "#10B981")
        self.banner = RoundedCard(
            self.inner,
            bg_color=banner_bg,
            border_color=p.get("accent", "#10B981"),
            parent_bg=bg,
            radius=8,
            inset=5,
            height=28
        )
        self.banner.pack(fill="x")

        conn_status = "Connected" if is_connected else "Ready"
        self.lbl_banner = tk.Label(
            self.banner.inner,
            text=f"● {device_name} • {conn_status} ({battery}% Battery)",
            font=("Segoe UI", 7, "bold"),
            fg=banner_fg,
            bg=banner_bg,
            anchor="w"
        )
        self.lbl_banner.pack(fill="x")

        self.vitals_inner = tk.Frame(self.inner, bg=bg, pady=6)
        self.vitals_inner.pack(fill="both", expand=True)

        self.vitals_grid = tk.Frame(self.vitals_inner, bg=bg)
        self.vitals_grid.pack(fill="x")
        self.vitals_grid.columnconfigure((0, 1), weight=1)

        self.btn_row = tk.Frame(self.vitals_inner, bg=bg)
        self.btn_row.pack(fill="x", pady=(6, 0))

        self.update_vitals(device_name, battery, is_connected, vitals or {})

    def update_vitals(self, device_name: str, battery: int, is_connected: bool, vitals: Dict[str, Any]):
        p = self.p
        bg = p.get("surface", "#171B24")
        text_pri = p.get("text_primary", "#F8FAFC")
        text_sec = p.get("text_secondary", "#94A3B8")

        conn_status = "Connected" if is_connected else "Ready"
        self.lbl_banner.config(text=f"● {device_name} • {conn_status} ({battery}% Battery)")

        for w in self.vitals_grid.winfo_children():
            w.destroy()

        r_hr = vitals.get("resting_hr") or 62
        bp_sys = vitals.get("bp_systolic") or 118
        bp_dia = vitals.get("bp_diastolic") or 76
        sleep_score = vitals.get("sleep_score") or 88
        steps = vitals.get("steps_count") or 9420

        # Pulse
        c1 = tk.Frame(self.vitals_grid, bg=bg, pady=3)
        c1.grid(row=0, column=0, sticky="w")
        tk.Label(c1, text="RESTING PULSE", font=("Segoe UI", 7, "bold"), fg=text_sec, bg=bg).pack(anchor="w")
        tk.Label(c1, text=f"{r_hr} BPM", font=("Segoe UI", 11, "bold"), fg=text_pri, bg=bg).pack(anchor="w")

        # BP
        c2 = tk.Frame(self.vitals_grid, bg=bg, pady=3)
        c2.grid(row=0, column=1, sticky="w")
        tk.Label(c2, text="BLOOD PRESSURE", font=("Segoe UI", 7, "bold"), fg=text_sec, bg=bg).pack(anchor="w")
        tk.Label(c2, text=f"{bp_sys}/{bp_dia} mmHg", font=("Segoe UI", 11, "bold"), fg=text_pri, bg=bg).pack(anchor="w")

        # Sleep
        c3 = tk.Frame(self.vitals_grid, bg=bg, pady=3)
        c3.grid(row=1, column=0, sticky="w")
        tk.Label(c3, text="SLEEP SCORE", font=("Segoe UI", 7, "bold"), fg=text_sec, bg=bg).pack(anchor="w")
        tk.Label(c3, text=f"{sleep_score}/100 Restored", font=("Segoe UI", 11, "bold"), fg=text_pri, bg=bg).pack(anchor="w")

        # Steps
        c4 = tk.Frame(self.vitals_grid, bg=bg, pady=3)
        c4.grid(row=1, column=1, sticky="w")
        tk.Label(c4, text="DAILY STEPS", font=("Segoe UI", 7, "bold"), fg=text_sec, bg=bg).pack(anchor="w")
        try:
            steps_int = int(steps)
            steps_text = f"{steps_int:,} Steps"
        except (ValueError, TypeError):
            steps_text = "9,420 Steps"
        tk.Label(c4, text=steps_text, font=("Segoe UI", 11, "bold"), fg=text_pri, bg=bg).pack(anchor="w")

        for w in self.btn_row.winfo_children():
            w.destroy()

        if self.on_sync:
            sync_btn = CurvyButton(
                self.btn_row,
                text="Sync Now",
                command=self.on_sync,
                bg_color=p.get("accent", "#10B981"),
                hover_color=p.get("accent_hover", "#059669"),
                fg_color="#FFFFFF",
                width=96,
                height=30,
                radius=14
            )
            sync_btn.pack(side="left")

        if self.on_manage:
            manage_btn = CurvyButton(
                self.btn_row,
                text="Manage Health",
                command=self.on_manage,
                bg_color=p.get("surface_hover", "#202633"),
                hover_color=p.get("border", "#334155"),
                fg_color=p.get("text_primary", "#F8FAFC"),
                border_color=p.get("border", "#26354A"),
                width=116,
                height=30,
                radius=14
            )
            manage_btn.pack(side="right")


class FloatingPillNav(tk.Frame):
    """Floating pill-shaped navigation container with active and inactive tabs."""

    def __init__(
        self,
        parent,
        items: List[tuple],
        active_key: str,
        on_select: Callable[[str], None],
        palette: Dict[str, str] = None,
        **kwargs
    ):
        p = palette or {}
        bg = p.get("bg", "#0D0E12")
        border = p.get("border", "#26354A")

        super().__init__(parent, bg=bg, **kwargs)
        self.p = p
        self.items = items
        self.active_key = active_key
        self.on_select = on_select
        self.buttons: Dict[str, tk.Label] = {}

        bar_bg = p.get("pill_bg", "#141D26")
        self.bar = tk.Frame(
            self,
            bg=bar_bg,
            highlightbackground=border,
            highlightthickness=1,
            padx=4,
            pady=4
        )
        self.bar.pack(anchor="center")

        for key, label in items:
            is_active = (key == active_key)
            lbl_bg = p.get("pill_active_bg", "#10B981") if is_active else bar_bg
            lbl_fg = p.get("pill_active_fg", "#FFFFFF") if is_active else p.get("text_secondary", "#94A3B8")

            lbl = tk.Label(
                self.bar,
                text=label,
                font=("Segoe UI", 9, "bold" if is_active else "normal"),
                fg=lbl_fg,
                bg=lbl_bg,
                padx=14,
                pady=5,
                cursor="hand2"
            )
            lbl.pack(side="left", padx=2)
            lbl.bind("<Button-1>", lambda e, k=key: self._handle_click(k))
            self.buttons[key] = lbl

    def _handle_click(self, key: str):
        self.active_key = key
        self.update_active(key)
        self.on_select(key)

    def update_active(self, active_key: str):
        p = self.p
        bar_bg = p.get("pill_bg", "#141D26")
        for key, lbl in self.buttons.items():
            is_active = (key == active_key)
            lbl_bg = p.get("pill_active_bg", "#10B981") if is_active else bar_bg
            lbl_fg = p.get("pill_active_fg", "#FFFFFF") if is_active else p.get("text_secondary", "#94A3B8")
            lbl.configure(
                bg=lbl_bg,
                fg=lbl_fg,
                font=("Segoe UI", 9, "bold" if is_active else "normal")
            )
