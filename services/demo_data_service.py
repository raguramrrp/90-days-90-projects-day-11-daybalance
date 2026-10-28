"""
DayBalance Demo Dataset Generator
Populates a realistic, mathematically coherent 60-day illustrative dataset
for immediate demonstration, exploration, and portfolio review.
"""

from datetime import date, datetime, timedelta
from pathlib import Path
import random
from typing import Any, Dict, List, Optional
from database.connection import get_db_connection
from database.repository import (
    add_wearable_device, create_experiment, create_focus_session, create_goal,
    create_habit, create_profile, create_routine,
    get_profiles, log_habit_entry, log_health_biometrics, log_lifestyle
)


DEMO_PROFILE_NAME = "Alex Morgan (Demo - Student & Builder)"


def seed_demo_profile(db_path: Optional[Path] = None, force_refresh: bool = False) -> int:
    """
    Creates or re-seeds the realistic 60-day demo profile.
    Uses deterministic pseudo-random sequences so results remain consistent and reproducible.
    """
    from database.migrations import init_db
    init_db(db_path)

    random.seed(42)

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM profiles WHERE name = ? AND is_demo = 1", (DEMO_PROFILE_NAME,))
        existing = cursor.fetchone()

        if existing:
            demo_id = existing[0]
            if not force_refresh:
                return demo_id
            # Clean up old demo profile data
            cursor.execute("DELETE FROM profiles WHERE id = ?", (demo_id,))

    # 1. Create Demo Profile
    profile_id = create_profile(
        name=DEMO_PROFILE_NAME,
        email="alex.builder@example.com",
        theme_preference="dark",
        quiet_hours_start="22:30",
        quiet_hours_end="06:30",
        is_demo=1,
        db_path=db_path
    )

    # 2. Create Routines
    morning_routine_id = create_routine(
        profile_id=profile_id,
        name="Morning Jumpstart",
        time_of_day="morning",
        description="Daily anchor routine to prime cognitive focus and physical energy.",
        order_index=1,
        db_path=db_path
    )

    evening_routine_id = create_routine(
        profile_id=profile_id,
        name="Evening Wind-down",
        time_of_day="evening",
        description="Reflection, screen disconnection, and sleep hygiene prep.",
        order_index=2,
        db_path=db_path
    )

    # 3. Create Habits
    sixty_days_ago = (date.today() - timedelta(days=60)).isoformat()

    h_study = create_habit(
        profile_id=profile_id,
        name="Deep Study & Problem Solving",
        category="Study & Academic",
        measurement_type="duration_minutes",
        target_value=120.0,
        unit="mins",
        frequency="daily",
        start_date=sixty_days_ago,
        routine_id=morning_routine_id,
        color="#0d9488",
        description="Focused machine learning problem sets, algorithms, or project building.",
        db_path=db_path
    )

    h_exercise = create_habit(
        profile_id=profile_id,
        name="Daily Movement & Workout",
        category="Movement & Active",
        measurement_type="duration_minutes",
        target_value=30.0,
        unit="mins",
        frequency="weekdays",
        frequency_days=[0, 1, 2, 3, 4],  # Mon-Fri
        start_date=sixty_days_ago,
        color="#14b8a6",
        description="Gym strength training, running, or brisk aerobic movement.",
        db_path=db_path
    )

    h_meditation = create_habit(
        profile_id=profile_id,
        name="Mindful Breathing & Stillness",
        category="Mindfulness & Well-being",
        measurement_type="duration_minutes",
        target_value=15.0,
        unit="mins",
        frequency="daily",
        start_date=sixty_days_ago,
        routine_id=morning_routine_id,
        color="#06b6d4",
        description="15 minutes unguided mindfulness to regulate nervous system.",
        db_path=db_path
    )

    h_reading = create_habit(
        profile_id=profile_id,
        name="Read Technical / Non-fiction",
        category="Productivity & Deep Work",
        measurement_type="count",
        target_value=20.0,
        unit="pages",
        frequency="daily",
        start_date=sixty_days_ago,
        color="#3b82f6",
        description="Reading books on distributed systems, AI architectures, or philosophy.",
        db_path=db_path
    )

    h_sleep_habit = create_habit(
        profile_id=profile_id,
        name="Sleep Consistency (7.5h+)",
        category="Health & Fitness",
        measurement_type="duration_minutes",
        target_value=450.0,
        unit="mins",
        frequency="daily",
        start_date=sixty_days_ago,
        routine_id=evening_routine_id,
        color="#8b5cf6",
        description="In bed by 11:00 PM to protect cognitive restoration.",
        db_path=db_path
    )

    h_screen = create_habit(
        profile_id=profile_id,
        name="Digital Sunset at 10 PM",
        category="Mindfulness & Well-being",
        measurement_type="boolean",
        target_value=1.0,
        unit="times",
        frequency="daily",
        start_date=sixty_days_ago,
        routine_id=evening_routine_id,
        color="#10b981",
        description="No phone or bright laptops in the bedroom 1 hour prior to sleep.",
        db_path=db_path
    )

    # 4. Register Paired Wearable Device & Generate 60 days of correlated history
    dev_id = add_wearable_device(
        profile_id=profile_id,
        device_name="Galaxy Watch6 Classic",
        device_type="smartwatch",
        device_brand="Samsung",
        device_model="SM-R960 (47mm)",
        mac_address="D4:8A:39:7C:12:F4",
        battery_level=84,
        is_connected=1,
        db_path=db_path
    )

    today = date.today()
    exercise_types = ["Strength Training", "Running", "Cardio / HIIT", "Bodyweight Flow", "Brisk Walk"]

    for day_offset in range(60, -1, -1):
        cur_date = today - timedelta(days=day_offset)
        cur_date_str = cur_date.isoformat()
        is_wknd = cur_date.weekday() >= 5

        # Lifestyle generation with realistic correlations:
        # Better sleep -> longer focus time; exercise -> higher mood & energy
        sleep_hours = round(random.gauss(7.4, 0.75), 1)
        sleep_hours = max(5.0, min(9.5, sleep_hours))

        # Sleep quality correlates with sleep hours
        quality_factor = (sleep_hours - 6.0) / 2.0
        sleep_quality = int(round(3 + quality_factor + random.uniform(-0.5, 0.5)))
        sleep_quality = max(1, min(5, sleep_quality))

        # Study minutes correlates with sleep hours and weekday
        base_study = 120 if not is_wknd else 70
        study_boost = (sleep_hours - 7.0) * 20.0
        study_minutes = int(round(base_study + study_boost + random.gauss(0, 20)))
        study_minutes = max(30, min(240, study_minutes))
        focus_sessions = max(1, study_minutes // 45)

        # Exercise: weekdays usually active, weekends occasional
        has_exercise = random.random() < 0.85 if not is_wknd else random.random() < 0.40
        exercise_mins = int(round(random.gauss(35, 10))) if has_exercise else 0
        exercise_mins = max(15, min(75, exercise_mins)) if has_exercise else 0
        ex_type = random.choice(exercise_types) if has_exercise else None

        # Mood & Energy: exercise and sleep boost them
        mood_base = 3.0 + (0.6 if has_exercise else 0.0) + (0.3 if sleep_hours >= 7.5 else -0.3)
        mood_score = int(round(mood_base + random.uniform(-0.4, 0.4)))
        mood_score = max(1, min(5, mood_score))

        energy_base = 2.8 + (0.8 if has_exercise else 0.0) + (0.4 if sleep_hours >= 7.5 else -0.4)
        energy_score = int(round(energy_base + random.uniform(-0.4, 0.4)))
        energy_score = max(1, min(5, energy_score))

        reflections = [
            "Good concentration during morning deep work.",
            "Felt well rested today; tackled hard algorithm problems.",
            "Afternoon slump after lunch; recovered with a short walk.",
            "Solid workout session; energy felt high in the evening.",
            "Late night review; made steady progress on DayBalance."
        ]
        reflection_notes = random.choice(reflections) if random.random() < 0.35 else None

        # Log lifestyle
        log_lifestyle(
            profile_id=profile_id,
            log_date=cur_date_str,
            sleep_hours=sleep_hours,
            sleep_quality=sleep_quality,
            study_minutes=study_minutes,
            focus_sessions_count=focus_sessions,
            exercise_minutes=exercise_mins,
            exercise_type=ex_type,
            mood_score=mood_score,
            energy_score=energy_score,
            reflection_notes=reflection_notes,
            db_path=db_path
        )

        # Log correlated health biometrics from wearable device
        base_rhr = 60 if has_exercise else 65
        resting_hr = int(round(base_rhr + (7.5 - sleep_hours) * 1.5 + random.uniform(-1.5, 1.5)))
        peak_hr = int(round(random.gauss(140, 6))) if has_exercise else int(round(random.gauss(108, 5)))
        avg_hr = int(round((resting_hr * 0.65) + (peak_hr * 0.35)))
        bp_sys = int(round(116 + (0 if has_exercise else 4) + random.uniform(-2, 2)))
        bp_dia = int(round(76 + random.uniform(-2, 2)))
        spo2 = int(round(98 + (1 if sleep_hours >= 7.5 else 0) + random.uniform(-0.5, 0.5)))
        spo2 = max(95, min(99, spo2))
        hrv = int(round(62 + (sleep_hours - 7.0) * 8 + (8 if has_exercise else 0) + random.uniform(-3, 3)))
        hrv = max(40, min(95, hrv))

        deep_sleep = int(round(sleep_hours * 13.5 + random.uniform(-5, 8)))
        rem_sleep = int(round(sleep_hours * 15.0 + random.uniform(-6, 8)))
        light_sleep = int(round((sleep_hours * 60) - deep_sleep - rem_sleep))
        sleep_score = int(round(72 + (sleep_hours - 6.0) * 8.0 + (5 if has_exercise else 0) + random.uniform(-2, 2)))
        sleep_score = max(60, min(98, sleep_score))

        steps = int(round(random.gauss(10400, 1100))) if has_exercise else int(round(random.gauss(5600, 700)))
        calories = int(round(steps * 0.045 + (exercise_mins * 7.5) + random.uniform(50, 100)))

        log_health_biometrics(
            profile_id=profile_id,
            log_date=cur_date_str,
            resting_hr=resting_hr,
            peak_hr=peak_hr,
            avg_hr=avg_hr,
            bp_systolic=bp_sys,
            bp_diastolic=bp_dia,
            spo2_pct=spo2,
            hrv_ms=hrv,
            deep_sleep_minutes=deep_sleep,
            rem_sleep_minutes=rem_sleep,
            light_sleep_minutes=light_sleep,
            sleep_score=sleep_score,
            steps_count=steps,
            active_calories=calories,
            device_id=dev_id,
            db_path=db_path
        )

        # Log habit entries:
        # In the most recent 12 days, maintain an active streak!
        in_recent_streak = day_offset <= 11

        # Habit 1: Study
        study_comp = in_recent_streak or (random.random() < 0.85)
        log_habit_entry(
            profile_id=profile_id,
            habit_id=h_study,
            entry_date=cur_date_str,
            status="completed" if study_comp else ("partial" if random.random() < 0.5 else "skipped"),
            value_recorded=study_minutes if study_comp else round(study_minutes * 0.5),
            target_at_entry=120.0,
            skip_reason=None if study_comp else "Campus exam prep / travel",
            db_path=db_path
        )

        # Habit 2: Exercise (weekday only)
        if cur_date.weekday() < 5:
            ex_comp = in_recent_streak or has_exercise
            log_habit_entry(
                profile_id=profile_id,
                habit_id=h_exercise,
                entry_date=cur_date_str,
                status="completed" if ex_comp else "rest_day",
                value_recorded=max(exercise_mins, 30) if ex_comp else 0.0,
                target_at_entry=30.0,
                skip_reason=None if ex_comp else "Active muscle recovery",
                db_path=db_path
            )

        # Habit 3: Meditation
        med_comp = in_recent_streak or (random.random() < 0.78)
        log_habit_entry(
            profile_id=profile_id,
            habit_id=h_meditation,
            entry_date=cur_date_str,
            status="completed" if med_comp else ("rest_day" if is_wknd else "skipped"),
            value_recorded=15.0 if med_comp else 0.0,
            target_at_entry=15.0,
            db_path=db_path
        )

        # Habit 4: Reading
        read_comp = in_recent_streak or (random.random() < 0.75)
        pages = int(round(random.gauss(22, 5))) if read_comp else int(round(random.gauss(8, 3)))
        log_habit_entry(
            profile_id=profile_id,
            habit_id=h_reading,
            entry_date=cur_date_str,
            status="completed" if read_comp else "partial",
            value_recorded=max(pages, 1),
            target_at_entry=20.0,
            db_path=db_path
        )

        # Habit 5: Sleep Habit
        sleep_comp = sleep_hours >= 7.25
        log_habit_entry(
            profile_id=profile_id,
            habit_id=h_sleep_habit,
            entry_date=cur_date_str,
            status="completed" if sleep_comp else "partial",
            value_recorded=round(sleep_hours * 60.0),
            target_at_entry=450.0,
            db_path=db_path
        )

        # Habit 6: Digital Sunset
        sunset_comp = in_recent_streak or (random.random() < 0.70)
        log_habit_entry(
            profile_id=profile_id,
            habit_id=h_screen,
            entry_date=cur_date_str,
            status="completed" if sunset_comp else "skipped",
            value_recorded=1.0 if sunset_comp else 0.0,
            target_at_entry=1.0,
            skip_reason=None if sunset_comp else "Late project deployment deadline",
            db_path=db_path
        )

    # 5. Create Goals
    create_goal(
        profile_id=profile_id,
        habit_id=h_study,
        title="Deep Work Consistency Sprint",
        target_metric="completion_rate",
        target_value=85.0,
        period_type="weekly",
        start_date=(today - timedelta(days=14)).isoformat(),
        end_date=(today + timedelta(days=14)).isoformat(),
        db_path=db_path
    )

    create_goal(
        profile_id=profile_id,
        habit_id=h_meditation,
        title="Mindfulness 14-Day Chain",
        target_metric="streak_days",
        target_value=14.0,
        period_type="challenge",
        start_date=(today - timedelta(days=10)).isoformat(),
        end_date=(today + timedelta(days=20)).isoformat(),
        db_path=db_path
    )

    # 6. Create Habit Experiment
    create_experiment(
        profile_id=profile_id,
        title="Morning Meditation vs Daily Study Duration",
        hypothesis="Consistent 15-minute morning mindfulness reduces task-switching latency and increases total daily deep work.",
        primary_metric="study_minutes",
        habit_id=h_meditation,
        baseline_start=(today - timedelta(days=40)).isoformat(),
        baseline_end=(today - timedelta(days=21)).isoformat(),
        intervention_start=(today - timedelta(days=20)).isoformat(),
        intervention_end=(today - timedelta(days=1)).isoformat(),
        db_path=db_path
    )

    # 7. Create Recent Focus Sessions
    for i in range(1, 6):
        session_date = (today - timedelta(days=i)).isoformat()
        create_focus_session(
            profile_id=profile_id,
            habit_id=h_study,
            task_name=f"LeetCode DP & Graph Exploration #{i}",
            duration_minutes=45,
            completed_at=f"{session_date}T10:30:00",
            notes="Zero distraction focus block; completed 2 medium problems.",
            db_path=db_path
        )

    return profile_id
