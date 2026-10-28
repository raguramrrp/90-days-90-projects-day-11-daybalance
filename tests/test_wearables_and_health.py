"""
Unit tests for Wearable Devices & Health Biometrics repository methods and telemetry.
"""

from database.repository import (
    add_wearable_device, create_profile, delete_wearable_device,
    get_health_biometrics, get_latest_health_biometrics,
    get_wearable_devices, log_health_biometrics
)


def test_wearable_device_lifecycle(test_db_path):
    p_id = create_profile("Biometric Tester", db_path=test_db_path)

    # 1. Add wearable device
    dev_id = add_wearable_device(
        profile_id=p_id,
        device_name="Galaxy Watch6 Classic",
        device_type="smartwatch",
        device_brand="Samsung",
        battery_level=84,
        is_connected=1,
        db_path=test_db_path
    )
    assert dev_id > 0

    # 2. Retrieve devices
    devices = get_wearable_devices(p_id, db_path=test_db_path)
    assert len(devices) == 1
    assert devices[0]["device_name"] == "Galaxy Watch6 Classic"
    assert devices[0]["battery_level"] == 84
    assert devices[0]["is_connected"] == 1

    # 3. Delete / unpair device
    deleted = delete_wearable_device(dev_id, p_id, db_path=test_db_path)
    assert deleted is True

    devices_after = get_wearable_devices(p_id, db_path=test_db_path)
    assert len(devices_after) == 0


def test_health_biometrics_logging_and_upsert(test_db_path):
    p_id = create_profile("Telemetry User", db_path=test_db_path)

    # 1. Log health biometrics
    row_id = log_health_biometrics(
        profile_id=p_id,
        log_date="2026-10-28",
        resting_hr=62,
        peak_hr=136,
        avg_hr=72,
        bp_systolic=118,
        bp_diastolic=76,
        spo2_pct=98,
        hrv_ms=64,
        deep_sleep_minutes=94,
        rem_sleep_minutes=108,
        light_sleep_minutes=263,
        sleep_score=88,
        steps_count=9420,
        active_calories=485,
        db_path=test_db_path
    )
    assert row_id > 0

    # 2. Retrieve latest
    latest = get_latest_health_biometrics(p_id, db_path=test_db_path)
    assert latest is not None
    assert latest["resting_hr"] == 62
    assert latest["bp_systolic"] == 118
    assert latest["bp_diastolic"] == 76
    assert latest["sleep_score"] == 88
    assert latest["steps_count"] == 9420

    # 3. Upsert / update same date with updated metrics
    log_health_biometrics(
        profile_id=p_id,
        log_date="2026-10-28",
        resting_hr=60,
        steps_count=10500,
        db_path=test_db_path
    )

    updated = get_latest_health_biometrics(p_id, db_path=test_db_path)
    assert updated["resting_hr"] == 60
    assert updated["steps_count"] == 10500
    # Preserved fields
    assert updated["bp_systolic"] == 118
    assert updated["sleep_score"] == 88


def test_health_biometrics_profile_isolation(test_db_path):
    p1 = create_profile("User One", db_path=test_db_path)
    p2 = create_profile("User Two", db_path=test_db_path)

    log_health_biometrics(profile_id=p1, log_date="2026-10-28", resting_hr=58, steps_count=8000, db_path=test_db_path)
    log_health_biometrics(profile_id=p2, log_date="2026-10-28", resting_hr=74, steps_count=4500, db_path=test_db_path)

    bio1 = get_latest_health_biometrics(p1, db_path=test_db_path)
    bio2 = get_latest_health_biometrics(p2, db_path=test_db_path)

    assert bio1["resting_hr"] == 58
    assert bio1["steps_count"] == 8000

    assert bio2["resting_hr"] == 74
    assert bio2["steps_count"] == 4500
