# DayBalance: Automated Testing Suite & Verification Matrix

---

## 1. Test Strategy Overview

DayBalance utilizes `pytest` to execute comprehensive unit and integration tests across data persistence, habit calculations, streaks, statistical modeling, insights, lifestyle validations, and backup recovery.

All tests utilize an isolated temporary SQLite database fixture (`test_db_path`), guaranteeing zero mutation or risk to user production data.

---

## 2. Test Execution Command

Run the automated test suite on Windows PowerShell:

```powershell
cd "D:\90 days\90-days-90-projects-day-11-daybalance"
.\.venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

Or execute the one-click batch runner:

```cmd
test.bat
```

---

## 3. Test Matrix & Results

| Module | Test Case | Status | Verification Scope |
| :--- | :--- | :--- | :--- |
| **`test_analytics.py`** | `test_sample_size_guard` | **PASS** | Enforces minimum sample size threshold ($n \ge 7$). |
| | `test_perfect_positive_correlation` | **PASS** | Validates $r = +1.0$ and $\rho = +1.0$ on linear paired series. |
| | `test_perfect_negative_correlation` | **PASS** | Validates $r = -1.0$ and $\rho = -1.0$ on inverse series. |
| | `test_constant_variable_zero_variance` | **PASS** | Handles zero variance without division-by-zero errors. |
| | `test_rolling_averages_calculation` | **PASS** | Verifies 7-day rolling window mean calculation. |
| **`test_backup_restore.py`**| `test_json_backup_and_restore_cycle` | **PASS** | Validates full JSON export and safe foreign-key remapping on restore. |
| | `test_csv_export_and_import` | **PASS** | Verifies CSV export and row-level validation during import. |
| **`test_experiments.py`** | `test_experiment_evaluation_math` | **PASS** | Verifies baseline vs intervention means, medians, and % delta. |
| | `test_experiment_insufficient_data` | **PASS** | Gracefully handles empty or non-overlapping date ranges. |
| **`test_focus_timer.py`** | `test_focus_session_logging_and_retrieval` | **PASS** | Verifies deep work session persistence and profile isolation. |
| **`test_insights.py`** | `test_empty_dataframe_initial_insight` | **PASS** | Returns friendly onboarding guidance on empty database. |
| | `test_peak_weekday_insight_trigger` | **PASS** | Surfaces peak weekday when completion spread $\ge 15\%$. |
| | `test_streak_milestone_insight_trigger` | **PASS** | Triggers milestone cards at 7, 14, 30 days. |
| **`test_lifestyle.py`** | `test_lifestyle_validation_ranges` | **PASS** | Validates boundaries for sleep (0-24h), study (0-1440m), mood/energy (1-5). |
| | `test_format_duration_hm` | **PASS** | Formats minute integers into readable hours/minutes. |
| | `test_summarize_lifestyle_logs` | **PASS** | Aggregates daily lifestyle records into accurate averages. |
| **`test_repository.py`**| `test_profile_lifecycle` | **PASS** | Profile creation, preference updates, and retrieval. |
| | `test_profile_isolation` | **PASS** | Queries for Profile A strictly never expose records of Profile B. |
| | `test_habit_crud_and_archival` | **PASS** | Habit creation, updating, and archival preservation. |
| | `test_habit_entry_upsert_and_target_preservation` | **PASS** | UPSERT logic and historical `target_at_entry` integrity. |
| | `test_profile_cascade_deletion` | **PASS** | Cascading deletion removes all child records cleanly. |
| **`test_streaks.py`** | `test_basic_daily_streak` | **PASS** | Contiguous daily habit completions form unbroken streak. |
| | `test_weekday_habit_does_not_break_over_weekend` | **PASS** | Weekday-only habits preserve streaks across unscheduled weekends. |
| | `test_rest_day_preserves_streak` | **PASS** | Explicitly marked rest days preserve active streak. |
| | `test_missed_day_breaks_current_streak_but_preserves_best_streak` | **PASS** | Missed days reset current streak without mutating best historical streak. |
| | `test_today_unlogged_grace` | **PASS** | Unlogged current day does not penalize streak completed yesterday. |

**Total Tests:** 26  
**Passed:** 26  
**Failed:** 0  
**Execution Time:** ~7.0 seconds
