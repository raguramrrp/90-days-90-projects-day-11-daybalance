"""
DayBalance Desktop Top Navigation Bar Component
Full-width top navigation bar matching the approved proposed design concept:
- Left: 'DAYBALANCE' logo in vibrant emerald with 'Your daily rhythm' subtitle.
- Center: Floating curvy rounded pill container with high-contrast pill tabs:
  Dashboard, Daily Check-in, Habits, Calendar, Analytics, Experiments, Focus Timer, Wearables, Settings.
- Right: Sleek ThemeToggleButton (vector Sun/Moon symbols) + Rounded Profile chip with ProfileLogo.
- Zero non-fire emojis; all boxes feature smooth rounded corners.
"""

import tkinter as tk
from typing import Callable, Dict, Optional
from desktop_app.components import CurvyButton, ProfileLogo, RoundedPillFrame, ThemeToggleButton


class TopNavigationBar(tk.Frame):
    def __init__(
        self,
        parent,
        on_navigate: Callable[[str], None],
        on_toggle_theme: Optional[Callable[[], None]] = None,
        palette: Dict[str, str] = None,
        profile_name: str = "Alex Morgan",
        current_theme: str = "dark",
        **kwargs
    ):
        p = palette or {}
        self.palette = p
        bg = p.get("bg", "#0D0E12")
        border = p.get("border_subtle", "#1B2330")
        self.on_navigate = on_navigate
        self.on_toggle_theme = on_toggle_theme
        self.active_key = "dashboard"
        self.profile_name = profile_name
        self.current_theme = current_theme

        super().__init__(
            parent,
            bg=bg,
            highlightbackground=border,
            highlightthickness=1,
            padx=18,
            pady=8,
            **kwargs
        )

        self.btn_map: Dict[str, tk.Label] = {}
        self._build_bar()

    def _build_bar(self):
        p = self.palette
        bg = p.get("bg", "#0D0E12")

        # 1. Left: Brand & Rhythm Logo
        brand_frame = tk.Frame(self, bg=bg)
        brand_frame.pack(side="left")

        brand_title = tk.Label(
            brand_frame,
            text="DAYBALANCE",
            font=("Segoe UI", 12, "bold"),
            fg=p.get("accent", "#10B981"),
            bg=bg,
            anchor="w"
        )
        brand_title.pack(anchor="w")

        brand_sub = tk.Label(
            brand_frame,
            text="Your daily rhythm",
            font=("Segoe UI", 8),
            fg=p.get("text_muted", "#64748B"),
            bg=bg,
            anchor="w"
        )
        brand_sub.pack(anchor="w")

        # 2. Right: Theme Toggle + Profile Chip (Right-aligned first so Center can center cleanly)
        right_box = tk.Frame(self, bg=bg)
        right_box.pack(side="right")

        # Smooth Rounded Profile Chip ($R=14px$)
        self.profile_chip = RoundedPillFrame(
            right_box,
            bg_color=p.get("surface", "#171B24"),
            border_color=p.get("border", "#26354A"),
            parent_bg=bg,
            radius=14,
            padx=6,
            pady=2
        )
        self.profile_chip.pack(side="right", padx=(8, 0))

        # Vector Profile Avatar Logo (Replaces 'AM' text badge!)
        self.profile_logo = ProfileLogo(
            self.profile_chip.inner,
            size=22,
            palette=p
        )
        self.profile_logo.pack(side="left", padx=(0, 5))

        clean_name = self.profile_name.split(" (")[0]
        self.lbl_profile = tk.Label(
            self.profile_chip.inner,
            text=clean_name,
            font=("Segoe UI", 9, "bold"),
            fg=p.get("text_primary", "#F8FAFC"),
            bg=p.get("surface", "#171B24")
        )
        self.lbl_profile.pack(side="left", padx=(0, 4))

        # Vector Theme Toggle Button (Sun in Dark Mode, Moon in Light Mode)
        if self.on_toggle_theme:
            self.theme_btn = ThemeToggleButton(
                right_box,
                is_dark=(self.current_theme == "dark"),
                command=self.on_toggle_theme,
                palette=p,
                width=42,
                height=26,
                radius=13
            )
            self.theme_btn.pack(side="right")

        # 3. Center: Floating Curvy Pill Navigation Container with Smooth Rounded Corners ($R=16px$)
        center_box = tk.Frame(self, bg=bg)
        center_box.pack(side="left", fill="both", expand=True)

        pill_container_bg = p.get("pill_container_bg", "#161D27" if self.current_theme == "dark" else "#F1F5F9")
        pill_container_border = p.get("pill_container_border", "#26354A" if self.current_theme == "dark" else "#E2E8F0")

        self.nav_pill_container = RoundedPillFrame(
            center_box,
            bg_color=pill_container_bg,
            border_color=pill_container_border,
            parent_bg=bg,
            radius=15,
            padx=3,
            pady=2
        )
        self.nav_pill_container.pack(anchor="center")
        self.nav_pill_frame = self.nav_pill_container.inner

        self.nav_items = [
            ("dashboard", "Dashboard"),
            ("checkin", "Daily Check-in"),
            ("habits", "Habits"),
            ("calendar", "Calendar"),
            ("analytics", "Analytics"),
            ("experiments", "Experiments"),
            ("timer", "Focus Timer"),
            ("wearables", "Wearables"),
            ("settings", "Settings")
        ]

        active_bg = p.get("pill_active_bg", "#10B981" if self.current_theme == "dark" else "#059669")
        active_fg = p.get("pill_active_fg", "#FFFFFF")
        inactive_fg = p.get("pill_inactive_fg", "#CBD5E1" if self.current_theme == "dark" else "#1E293B")

        for key, label in self.nav_items:
            is_active = (key == self.active_key)
            item_bg = active_bg if is_active else pill_container_bg
            item_fg = active_fg if is_active else inactive_fg

            lbl = tk.Label(
                self.nav_pill_frame,
                text=label,
                font=("Segoe UI", 8, "bold" if is_active else "normal"),
                fg=item_fg,
                bg=item_bg,
                padx=8,
                pady=3,
                cursor="hand2"
            )
            lbl.pack(side="left", padx=1)

            lbl.bind("<Button-1>", lambda e, k=key: self.select_item(k))
            lbl.bind("<Enter>", lambda e, l=lbl, k=key: self._on_hover(l, k))
            lbl.bind("<Leave>", lambda e, l=lbl, k=key: self._on_leave(l, k))

            self.btn_map[key] = lbl

    def select_item(self, key: str):
        self.active_key = key
        self._update_styles()
        self.on_navigate(key)

    def update_profile(self, name: str, streak: int = 44):
        self.profile_name = name
        clean_name = name.split(" (")[0]
        self.lbl_profile.config(text=clean_name)

    def _update_styles(self):
        p = self.palette
        pill_container_bg = p.get("pill_container_bg", "#161D27" if self.current_theme == "dark" else "#F1F5F9")
        active_bg = p.get("pill_active_bg", "#10B981" if self.current_theme == "dark" else "#059669")
        active_fg = p.get("pill_active_fg", "#FFFFFF")
        inactive_fg = p.get("pill_inactive_fg", "#CBD5E1" if self.current_theme == "dark" else "#1E293B")

        for key, lbl in self.btn_map.items():
            if key == self.active_key:
                lbl.configure(
                    bg=active_bg,
                    fg=active_fg,
                    font=("Segoe UI", 9, "bold")
                )
            else:
                lbl.configure(
                    bg=pill_container_bg,
                    fg=inactive_fg,
                    font=("Segoe UI", 9, "normal")
                )

    def _on_hover(self, lbl: tk.Label, key: str):
        if key != self.active_key:
            p = self.palette
            hover_bg = p.get("pill_hover_bg", "#202633" if self.current_theme == "dark" else "#E2E8F0")
            lbl.configure(
                bg=hover_bg,
                fg=p.get("text_primary", "#F8FAFC" if self.current_theme == "dark" else "#0F172A")
            )

    def _on_leave(self, lbl: tk.Label, key: str):
        if key != self.active_key:
            p = self.palette
            container_bg = p.get("pill_container_bg", "#161D27" if self.current_theme == "dark" else "#F1F5F9")
            inactive_fg = p.get("pill_inactive_fg", "#CBD5E1" if self.current_theme == "dark" else "#1E293B")
            lbl.configure(
                bg=container_bg,
                fg=inactive_fg
            )


# Backward compatibility alias so existing tests and imports succeed seamlessly
NavigationSidebar = TopNavigationBar
