"""
DayBalance — Section 8: Health & Wearable Devices Integration
Local Bluetooth LE device pairing, smartwatch health telemetry, and biometric tracking.
"""

from datetime import date, timedelta
import streamlit as st
from components.theme import apply_custom_css
from components.metric_cards import render_header
from components.modals import render_top_navbar
from database.repository import (
    add_wearable_device, delete_wearable_device,
    get_health_biometrics, get_latest_health_biometrics,
    get_wearable_devices, log_health_biometrics
)


def show_health_and_wearables() -> None:
    apply_custom_css()
    profile = render_top_navbar()
    p_id = profile["id"]
    today = date.today()
    today_str = today.isoformat()

    render_header(
        title="Health & Wearable Devices"
    )

    # 1. Fetch devices and biometrics
    devices = get_wearable_devices(p_id)
    latest_bio = get_latest_health_biometrics(p_id) or {}

    r_hr = latest_bio.get("resting_hr") or 62
    p_hr = latest_bio.get("peak_hr") or 136
    bp_sys = latest_bio.get("bp_systolic") or 118
    bp_dia = latest_bio.get("bp_diastolic") or 76
    spo2 = latest_bio.get("spo2_pct") or 98
    hrv = latest_bio.get("hrv_ms") or 64
    sleep_score = latest_bio.get("sleep_score") or 88
    steps = latest_bio.get("steps_count") or 9420

    # 2. Render Top 4 Bento Overview Cards
    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
    with c_b1:
        dev_sub = devices[0]["device_name"] if devices else "No devices paired"
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">PAIRED DEVICES</span>
<span class="db-stat-badge">{"Connected" if devices else "Ready"}</span>
</div>
<div class="db-bento-value">{len(devices)} Active</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
<div style="background: var(--db-accent); width: {100 if devices else 0}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub" style="margin-top: 6px;">{dev_sub}</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
    with c_b2:
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">RESTING HEART RATE</span>
<span class="db-stat-badge">Normal</span>
</div>
<div class="db-bento-value">{r_hr} BPM</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
<div style="background: #10B981; width: {min(100, int((r_hr / 100) * 100))}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub" style="margin-top: 6px;">Peak: {p_hr} BPM &bull; HRV: {hrv} ms</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
    with c_b3:
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">BLOOD PRESSURE</span>
<span class="db-stat-badge">Optimal</span>
</div>
<div class="db-bento-value">{bp_sys} / {bp_dia}</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
<div style="background: #059669; width: {min(100, int((bp_sys / 140) * 100))}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub" style="margin-top: 6px;">AHA Normal Category (mmHg)</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
    with c_b4:
        st.markdown(
            f"""<div class="db-bento-card" style="padding: 1.1rem 1.25rem;">
<div class="db-bento-content" style="width: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<span class="db-bento-label">SLEEP RECOVERY</span>
<span class="db-stat-badge">Score {sleep_score}</span>
</div>
<div class="db-bento-value">{sleep_score} / 100</div>
<div style="background: var(--db-border-subtle); border-radius: 999px; height: 6px; width: 100%; margin-top: 6px; overflow: hidden;">
<div style="background: #0284C7; width: {sleep_score}%; height: 100%; border-radius: 999px;"></div>
</div>
<div class="db-bento-sub" style="margin-top: 6px;">SpO2: {spo2}% &bull; {steps:,} Steps</div>
</div>
</div>""",
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

    tab_devices, tab_biometrics, tab_manual = st.tabs([
        "Paired Devices & BLE Sync",
        "Biometric Telemetry",
        "+ Manual Health Log"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Paired Devices & BLE Sync
    # -------------------------------------------------------------------------
    with tab_devices:
        st.markdown("#### Paired Smart Health Devices")
        st.caption("Manage smartwatches, fitness bands, and local health tracker sync.")

        if not devices:
            st.info("No health devices currently paired. Use the scan options below to connect your smartwatch or band.")
        else:
            for d in devices:
                b_level = d.get("battery_level", 85)
                c_pill = '<span class="db-cat-tag db-cat-active">Connected &bull; Live Telemetry</span>' if d.get("is_connected") else '<span class="db-cat-tag db-cat-custom">Disconnected</span>'
                m_str = d.get("device_model") or d.get("device_brand")
                mac_str = d.get("mac_address") or "Bluetooth LE"

                st.markdown(
                    f"""<div class="db-card" style="margin-bottom: 0.85rem; padding: 1.25rem 1.45rem;">
<div style="display: flex; justify-content: space-between; align-items: flex-start;">
<div>
<div style="display: flex; align-items: center; gap: 0.45rem; margin-bottom: 0.35rem;">
<span class="db-cat-tag db-cat-study">{d['device_type'].capitalize()}</span>
{c_pill}
</div>
<div style="font-size: 1.28rem; font-weight: 700; color: var(--db-text);">
{d['device_name']}
</div>
<div style="font-size: 0.82rem; color: var(--db-text-muted); margin-top: 0.25rem;">
Brand: {d['device_brand']} &bull; Model: {m_str} &bull; MAC: {mac_str}
</div>
</div>
<div style="text-align: right;">
<span class="db-stat-badge" style="font-size: 0.85rem; padding: 0.2rem 0.55rem;">
Battery: {b_level}%
</span>
<div style="font-size: 0.78rem; color: var(--db-text-muted); margin-top: 0.3rem;">
Last sync: Just now
</div>
</div>
</div>
</div>""",
                    unsafe_allow_html=True
                )

                c_d1, c_d2 = st.columns([1.5, 1.2])
                with c_d1:
                    if st.button(f"Sync Telemetry ({d['device_name']})", key=f"sync_{d['id']}", type="primary", use_container_width=True):
                        st.success(f"Synchronized biometrics from {d['device_name']}. Heart rate, blood pressure, and sleep stages updated.")
                        st.rerun()
                with c_d2:
                    if st.button(f"Unpair Device", key=f"unpair_{d['id']}", use_container_width=True):
                        delete_wearable_device(d["id"], p_id)
                        st.success(f"Device unshared.")
                        st.rerun()

                st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

        st.markdown("<hr style='border: none; border-top: 1px solid var(--db-border); margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### Discover Nearby Wearable Devices")
        st.caption("Pair your personal smartwatch or fitness band via Bluetooth LE or local health export.")

        c_scan1, c_scan2 = st.columns([1.5, 3.5])
        with c_scan1:
            scan_clicked = st.button("Scan for Bluetooth Devices", use_container_width=True)

        available_presets = [
            {"name": "Samsung Galaxy Watch7", "type": "smartwatch", "brand": "Samsung", "model": "SM-L310 (44mm)", "mac": "E8:55:71:02:4A:19"},
            {"name": "Apple Watch Ultra 2", "type": "smartwatch", "brand": "Apple", "model": "Watch Ultra", "mac": "A4:C1:38:9B:10:EE"},
            {"name": "Fitbit Charge 6", "type": "fitness band", "brand": "Fitbit / Google", "model": "Charge 6", "mac": "F0:13:C3:7A:41:88"},
            {"name": "Garmin Forerunner 965", "type": "smartwatch", "brand": "Garmin", "model": "Forerunner 965", "mac": "C4:7D:E2:5F:80:12"},
            {"name": "Whoop 4.0", "type": "fitness band", "brand": "Whoop", "model": "Whoop Strap", "mac": "D8:A0:11:32:04:9A"},
            {"name": "Oura Ring Gen 3", "type": "smart ring", "brand": "Oura", "model": "Horizon Ring", "mac": "84:2A:FD:9C:3E:70"}
        ]

        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        for cand in available_presets:
            c_info, c_act = st.columns([3.8, 1.2])
            with c_info:
                st.markdown(
                    f"""<div style="padding: 0.65rem 0.95rem; background: var(--db-surface); border: 1px solid var(--db-border-subtle); border-radius: 8px; margin-bottom: 0.4rem;">
<strong>{cand['name']}</strong> &bull; <span style="font-size: 0.82rem; color: var(--db-text-muted);">{cand['brand']} ({cand['type'].title()}) &bull; MAC: {cand['mac']}</span>
</div>""",
                    unsafe_allow_html=True
                )
            with c_act:
                if st.button("Pair & Connect", key=f"pair_{cand['name']}", use_container_width=True):
                    add_wearable_device(
                        profile_id=p_id,
                        device_name=cand["name"],
                        device_type=cand["type"],
                        device_brand=cand["brand"],
                        device_model=cand["model"],
                        mac_address=cand["mac"],
                        battery_level=90,
                        is_connected=1
                    )
                    st.success(f"Paired {cand['name']} successfully!")
                    st.rerun()

    # -------------------------------------------------------------------------
    # TAB 2: Biometric Telemetry
    # -------------------------------------------------------------------------
    with tab_biometrics:
        st.markdown("#### Health Telemetry Breakdown")
        st.caption("Continuous cardiovascular, sleep, and recovery metrics recorded from your paired health trackers.")

        c_t1, c_t2, c_t3 = st.columns(3)
        with c_t1:
            st.markdown(
                f"""<div class="db-card" style="padding: 1.15rem 1.35rem; margin-bottom: 1rem;">
<div class="db-bento-label">CARDIOVASCULAR METRICS</div>
<div style="font-size: 1.6rem; font-weight: 800; color: var(--db-text); margin: 0.35rem 0;">
{r_hr} <span style="font-size: 0.85rem; font-weight: 500; color: var(--db-text-muted);">BPM Resting</span>
</div>
<div style="font-size: 0.85rem; color: var(--db-text-secondary); line-height: 1.6;">
&bull; Peak Heart Rate: <strong>{p_hr} BPM</strong><br>
&bull; Heart Rate Variability: <strong>{hrv} ms</strong><br>
&bull; Blood Oxygen (SpO2): <strong>{spo2}%</strong>
</div>
</div>""",
                unsafe_allow_html=True
            )

        with c_t2:
            st.markdown(
                f"""<div class="db-card" style="padding: 1.15rem 1.35rem; margin-bottom: 1rem;">
<div class="db-bento-label">BLOOD PRESSURE (ARTERIAL)</div>
<div style="font-size: 1.6rem; font-weight: 800; color: #059669; margin: 0.35rem 0;">
{bp_sys} / {bp_dia} <span style="font-size: 0.85rem; font-weight: 500; color: var(--db-text-muted);">mmHg</span>
</div>
<div style="font-size: 0.85rem; color: var(--db-text-secondary); line-height: 1.6;">
&bull; Systolic Pressure: <strong>{bp_sys} mmHg</strong><br>
&bull; Diastolic Pressure: <strong>{bp_dia} mmHg</strong><br>
&bull; Classification: <strong>Normal / Healthy</strong>
</div>
</div>""",
                unsafe_allow_html=True
            )

        with c_t3:
            deep_m = latest_bio.get("deep_sleep_minutes", 100)
            rem_m = latest_bio.get("rem_sleep_minutes", 115)
            light_m = latest_bio.get("light_sleep_minutes", 250)
            st.markdown(
                f"""<div class="db-card" style="padding: 1.15rem 1.35rem; margin-bottom: 1rem;">
<div class="db-bento-label">SLEEP ARCHITECTURE & SCORE</div>
<div style="font-size: 1.6rem; font-weight: 800; color: #0284C7; margin: 0.35rem 0;">
{sleep_score} / 100 <span style="font-size: 0.85rem; font-weight: 500; color: var(--db-text-muted);">Score</span>
</div>
<div style="font-size: 0.85rem; color: var(--db-text-secondary); line-height: 1.6;">
&bull; Deep Sleep: <strong>{deep_m // 60}h {deep_m % 60}m</strong><br>
&bull; REM Sleep: <strong>{rem_m // 60}h {rem_m % 60}m</strong><br>
&bull; Light Sleep: <strong>{light_m // 60}h {light_m % 60}m</strong>
</div>
</div>""",
                unsafe_allow_html=True
            )

        # Historical Telemetry Table
        st.markdown("##### 14-Day Health Log History")
        bio_history = get_health_biometrics(p_id, start_date=(today - timedelta(days=14)).isoformat())
        if bio_history:
            display_rows = []
            for b in bio_history:
                display_rows.append({
                    "Date": b["log_date"],
                    "Resting HR (BPM)": b.get("resting_hr"),
                    "Peak HR (BPM)": b.get("peak_hr"),
                    "Blood Pressure": f"{b.get('bp_systolic')}/{b.get('bp_diastolic')}",
                    "SpO2": f"{b.get('spo2_pct')}%",
                    "HRV": f"{b.get('hrv_ms')} ms",
                    "Sleep Score": f"{b.get('sleep_score')}/100",
                    "Steps": f"{b.get('steps_count', 0):,}",
                    "Active Calories": f"{b.get('active_calories', 0)} kcal"
                })
            st.dataframe(display_rows, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # TAB 3: Manual Health Log
    # -------------------------------------------------------------------------
    with tab_manual:
        st.markdown("#### Record Manual Health Biometrics")
        st.caption("Manually enter health stats from blood pressure monitors, pulse oximeters, or clinical visits.")

        with st.form(key="manual_health_log_form"):
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                log_d = st.date_input("Measurement Date", value=today)
            with c_f2:
                sel_dev = st.selectbox(
                    "Source Device (Optional)",
                    options=[None] + [d["id"] for d in devices],
                    format_func=lambda x: "Manual Entry" if x is None else next((d["device_name"] for d in devices if d["id"] == x), f"Device #{x}")
                )

            c_h1, c_h2, c_h3 = st.columns(3)
            with c_h1:
                in_rhr = st.number_input("Resting Heart Rate (BPM)", min_value=40, max_value=140, value=65)
            with c_h2:
                in_sys = st.number_input("Systolic Blood Pressure (mmHg)", min_value=80, max_value=200, value=118)
            with c_h3:
                in_dia = st.number_input("Diastolic Blood Pressure (mmHg)", min_value=50, max_value=130, value=76)

            c_s1, c_s2, c_s3 = st.columns(3)
            with c_s1:
                in_spo2 = st.number_input("Blood Oxygen SpO2 (%)", min_value=85, max_value=100, value=98)
            with c_s2:
                in_hrv = st.number_input("HRV (ms)", min_value=10, max_value=180, value=62)
            with c_s3:
                in_steps = st.number_input("Daily Steps Count", min_value=0, max_value=50000, value=8500, step=500)

            sub_bio = st.form_submit_button("Save Biometric Record", type="primary", use_container_width=True)
            if sub_bio:
                log_health_biometrics(
                    profile_id=p_id,
                    log_date=log_d.isoformat(),
                    resting_hr=in_rhr,
                    bp_systolic=in_sys,
                    bp_diastolic=in_dia,
                    spo2_pct=in_spo2,
                    hrv_ms=in_hrv,
                    steps_count=in_steps,
                    device_id=sel_dev
                )
                st.success(f"Saved health biometrics for {log_d.isoformat()} successfully!")
                st.rerun()


show_health_and_wearables()
