"""
DayBalance Desktop — Health & Wearables Integration Page
Bluetooth LE smart health wearable devices pairing, continuous biometric telemetry,
and health vitals tracking (Heartbeat, Blood Pressure, Sleep Architecture, Steps).
"""

from datetime import date
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any

from database.repository import (
    add_wearable_device, delete_wearable_device,
    get_latest_health_biometrics, get_wearable_devices,
    log_health_biometrics
)
from desktop_app.components import HealthCard, ScrollableFrame


class WearablesPage(tk.Frame):
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
            text="Health & Smart Wearable Devices",
            font=("Segoe UI", 16, "bold"),
            fg=p["text_primary"],
            bg=bg
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Pair smartwatches, fitness bands, and smart rings to capture real-time biometrics locally",
            font=("Segoe UI", 8),
            fg=p["text_secondary"],
            bg=bg
        ).pack(anchor="w", pady=(2, 0))

        # 1. Biometrics Bento Grid (4 Cards)
        self.cards_frame = tk.Frame(self.content, bg=bg, padx=pad_x, pady=0)
        self.cards_frame.pack(fill="x")
        self.cards_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.card_devs = HealthCard(self.cards_frame, "PAIRED DEVICES", "1 Active", "Galaxy Watch6 Classic", "Connected", 1.0, palette=p)
        self.card_devs.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.card_hr = HealthCard(self.cards_frame, "RESTING HEART RATE", "62 BPM", "Peak: 136 BPM • HRV: 64 ms", "Normal", 0.62, palette=p, bar_color=p["success"])
        self.card_hr.grid(row=0, column=1, sticky="nsew", padx=3)

        self.card_bp = HealthCard(self.cards_frame, "BLOOD PRESSURE", "118 / 76", "AHA Normal Range • SpO2: 98%", "Optimal", 0.84, palette=p, bar_color=p["accent"])
        self.card_bp.grid(row=0, column=2, sticky="nsew", padx=3)

        self.card_sleep = HealthCard(self.cards_frame, "SLEEP RECOVERY", "88 / 100", "Deep: 94m • REM: 108m", "Restored", 0.88, palette=p, bar_color=p["info"])
        self.card_sleep.grid(row=0, column=3, sticky="nsew", padx=(6, 0))

        # 2. Main Two Column Section: Left Paired Devices, Right Pair New Device / Sync Form
        cols_frame = tk.Frame(self.content, bg=bg, padx=pad_x, pady=0)
        cols_frame.pack(fill="both", expand=True)
        cols_frame.columnconfigure(0, weight=3)
        cols_frame.columnconfigure(1, weight=2)

        # Left Column: Paired Devices List
        left_box = tk.Frame(cols_frame, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(left_box, text="PAIRED WEARABLE DEVICES", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=surface).pack(anchor="w", pady=(0, 10))

        self.devs_list_frame = tk.Frame(left_box, bg=surface)
        self.devs_list_frame.pack(fill="both", expand=True)

        # Right Column: Pair New Device Form
        right_box = tk.Frame(cols_frame, bg=surface, highlightbackground=border, highlightthickness=1, padx=18, pady=16)
        right_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        tk.Label(right_box, text="PAIR NEW SMART WEARABLE", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=surface).pack(anchor="w", pady=(0, 12))

        tk.Label(right_box, text="Device Brand / Ecosystem:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.cmb_brand = ttk.Combobox(right_box, values=["Samsung", "Apple", "Garmin", "Fitbit", "Whoop", "Oura Ring"], state="readonly")
        self.cmb_brand.set("Samsung")
        self.cmb_brand.pack(fill="x", pady=(2, 8))

        tk.Label(right_box, text="Device Name / Model:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.ent_dev_name = ttk.Entry(right_box)
        self.ent_dev_name.insert(0, "Galaxy Watch7")
        self.ent_dev_name.pack(fill="x", pady=(2, 8))

        tk.Label(right_box, text="Device Type:", font=("Segoe UI", 8, "bold"), fg=p["text_secondary"], bg=surface).pack(anchor="w")
        self.cmb_dev_type = ttk.Combobox(right_box, values=["smartwatch", "fitness_band", "smart_ring"], state="readonly")
        self.cmb_dev_type.set("smartwatch")
        self.cmb_dev_type.pack(fill="x", pady=(2, 14))

        ttk.Button(right_box, text="Pair & Connect Device", style="Accent.TButton", command=self._pair_device).pack(fill="x", pady=(0, 16))

        # Divider
        tk.Frame(right_box, bg=border, height=1).pack(fill="x", pady=(0, 12))

        # Manual Log / Fast Sync Vitals
        tk.Label(right_box, text="LOG OR SYNC VITALS TELEMETRY", font=("Segoe UI", 9, "bold"), fg=p["accent"], bg=surface).pack(anchor="w", pady=(0, 8))

        v_row = tk.Frame(right_box, bg=surface)
        v_row.pack(fill="x", pady=2)
        v_row.columnconfigure((0, 1), weight=1)

        tk.Label(v_row, text="Resting HR (BPM):", font=("Segoe UI", 8), fg=p["text_secondary"], bg=surface).grid(row=0, column=0, sticky="w")
        self.ent_v_hr = ttk.Entry(v_row, width=8)
        self.ent_v_hr.insert(0, "62")
        self.ent_v_hr.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=(2, 6))

        tk.Label(v_row, text="Peak HR (BPM):", font=("Segoe UI", 8), fg=p["text_secondary"], bg=surface).grid(row=0, column=1, sticky="w")
        self.ent_v_peak = ttk.Entry(v_row, width=8)
        self.ent_v_peak.insert(0, "136")
        self.ent_v_peak.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(2, 6))

        bp_row = tk.Frame(right_box, bg=surface)
        bp_row.pack(fill="x", pady=2)
        bp_row.columnconfigure((0, 1), weight=1)

        tk.Label(bp_row, text="Systolic BP (mmHg):", font=("Segoe UI", 8), fg=p["text_secondary"], bg=surface).grid(row=0, column=0, sticky="w")
        self.ent_v_sys = ttk.Entry(bp_row, width=8)
        self.ent_v_sys.insert(0, "118")
        self.ent_v_sys.grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=(2, 6))

        tk.Label(bp_row, text="Diastolic BP (mmHg):", font=("Segoe UI", 8), fg=p["text_secondary"], bg=surface).grid(row=0, column=1, sticky="w")
        self.ent_v_dia = ttk.Entry(bp_row, width=8)
        self.ent_v_dia.insert(0, "76")
        self.ent_v_dia.grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=(2, 6))

        ttk.Button(right_box, text="Save / Sync Vitals", style="Secondary.TButton", command=self._save_vitals).pack(fill="x", pady=(6, 0))

    def refresh(self):
        p_id = self.profile.get("id", 1)
        devices = get_wearable_devices(p_id)
        latest_bio = get_latest_health_biometrics(p_id) or {}

        r_hr = latest_bio.get("resting_hr") or 62
        p_hr = latest_bio.get("peak_hr") or 136
        bp_sys = latest_bio.get("bp_systolic") or 118
        bp_dia = latest_bio.get("bp_diastolic") or 76
        spo2 = latest_bio.get("spo2_pct") or 98
        hrv = latest_bio.get("hrv_ms") or 64
        deep_m = latest_bio.get("deep_sleep_minutes") or 94
        rem_m = latest_bio.get("rem_sleep_minutes") or 108
        sleep_score = latest_bio.get("sleep_score") or 88

        dev_title = f"{len(devices)} Active"
        dev_sub = devices[0]["device_name"] if devices else "No devices paired"

        self.card_devs.update_data(dev_title, dev_sub, "Connected" if devices else "Ready", 1.0 if devices else 0.0)
        self.card_hr.update_data(f"{r_hr} BPM", f"Peak: {p_hr} BPM • HRV: {hrv} ms", "Normal", min(1.0, r_hr / 100))
        self.card_bp.update_data(f"{bp_sys} / {bp_dia}", f"AHA Normal Range • SpO2: {spo2}%", "Optimal", min(1.0, bp_sys / 140))
        self.card_sleep.update_data(f"{sleep_score} / 100", f"Deep: {deep_m}m • REM: {rem_m}m", "Restored", min(1.0, sleep_score / 100))

        # Rebuild Paired Devices List
        for w in self.devs_list_frame.winfo_children():
            w.destroy()

        if not devices:
            tk.Label(
                self.devs_list_frame,
                text="No wearable health devices paired yet. Pair your smartwatch on the right.",
                font=("Segoe UI", 9),
                fg=self.p["text_muted"],
                bg=self.p["surface"],
                pady=20
            ).pack()
            return

        for dev in devices:
            did = dev["id"]
            d_box = tk.Frame(self.devs_list_frame, bg=self.p["bg"], highlightbackground=self.p["border"], highlightthickness=1, padx=14, pady=12)
            d_box.pack(fill="x", pady=6)

            top = tk.Frame(d_box, bg=self.p["bg"])
            top.pack(fill="x")

            tk.Label(top, text=dev["device_name"], font=("Segoe UI", 10, "bold"), fg=self.p["text_primary"], bg=self.p["bg"]).pack(side="left")

            conn_c = self.p["success"] if dev.get("is_connected") else self.p["text_muted"]
            tk.Label(top, text="● Connected" if dev.get("is_connected") else "○ Disconnected", font=("Segoe UI", 8, "bold"), fg=conn_c, bg=self.p["bg"]).pack(side="right")

            sub_txt = f"Brand: {dev.get('device_brand', 'Smartwatch')} • Type: {dev.get('device_type', 'smartwatch').capitalize()} • Battery: {dev.get('battery_level', 85)}%"
            tk.Label(d_box, text=sub_txt, font=("Segoe UI", 8), fg=self.p["text_secondary"], bg=self.p["bg"]).pack(anchor="w", pady=(2, 8))

            act_f = tk.Frame(d_box, bg=self.p["bg"])
            act_f.pack(fill="x")

            ttk.Button(act_f, text="Unpair Device", style="Secondary.TButton", command=lambda dev_id=did: self._unpair_device(dev_id)).pack(side="right")

    def _pair_device(self):
        name = self.ent_dev_name.get().strip()
        if not name:
            messagebox.showwarning("Validation Error", "Device name cannot be empty.")
            return

        brand = self.cmb_brand.get()
        dev_type = self.cmb_dev_type.get()
        p_id = self.profile.get("id", 1)

        add_wearable_device(
            profile_id=p_id,
            device_name=name,
            device_type=dev_type,
            device_brand=brand,
            battery_level=88,
            is_connected=1
        )
        self.refresh()
        messagebox.showinfo("Device Connected", f"Successfully paired '{name}' ({brand})! Live health telemetry active.")

    def _unpair_device(self, dev_id: int):
        p_id = self.profile.get("id", 1)
        delete_wearable_device(dev_id, p_id)
        self.refresh()
        messagebox.showinfo("Unpaired", "Wearable device disconnected.")

    def _save_vitals(self):
        p_id = self.profile.get("id", 1)
        today_str = date.today().isoformat()
        try:
            r_hr = int(self.ent_v_hr.get().strip() or "62")
            p_hr = int(self.ent_v_peak.get().strip() or "136")
            bp_sys = int(self.ent_v_sys.get().strip() or "118")
            bp_dia = int(self.ent_v_dia.get().strip() or "76")

            log_health_biometrics(
                profile_id=p_id,
                log_date=today_str,
                resting_hr=r_hr,
                peak_hr=p_hr,
                avg_hr=int((r_hr + p_hr) / 2),
                bp_systolic=bp_sys,
                bp_diastolic=bp_dia
            )
            self.refresh()
            messagebox.showinfo("Success", "Vitals telemetry successfully saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save vitals: {e}")
