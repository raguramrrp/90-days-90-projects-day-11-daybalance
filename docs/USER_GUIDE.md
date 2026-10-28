# DayBalance: Complete User Guide

A step-by-step operational manual for managing habits, logging daily metrics, exploring statistics, and configuring profiles in DayBalance.

---

## 1. Application Navigation

DayBalance features a compact, high-efficiency sidebar with 9 main sections:

1. **Dashboard**: High-level daily summary, 4 key metrics, trend graphs, and today's habit status.
2. **Daily Check-in**: Fast logging interface for today's habits, sleep, study, exercise, mood, and reflection.
3. **Habits & Routines**: Create custom habits, group habits into morning/evening stacks, edit targets, or archive habits.
4. **Calendar & History**: Date-based audit matrix, status filter, and entry correction inspector.
5. **Analytics & Insights**: Bivariate Pearson/Spearman correlation explorer, weekday rhythm graphs, and data-driven insights.
6. **Goals & Experiments**: Set weekly/monthly milestones and evaluate A/B lifestyle hypotheses.
7. **Focus Timer**: Configurable Pomodoro / deep-work block timer that saves completed sessions to your study records.
8. **Reports & Data**: Weekly executive digest, CSV exports, CSV import with validation, and complete JSON backups.
9. **Settings & Profiles**: Multi-profile switcher, profile preferences, quiet hours, and demo data tools.

---

## 2. Managing Habits & Routines

### Creating a Habit
1. Navigate to **Habits & Routines** ➔ Select **+ Create New Habit**.
2. Fill in:
   - **Name**: e.g. "Deep Study & Problem Solving"
   - **Category**: Health & Fitness, Study & Academic, Productivity, Movement, Mindfulness, or Custom.
   - **Measurement Type**:
     - *Completion (Yes/No)*: Boolean checkbox.
     - *Duration (Minutes)*: Numeric input in minutes.
     - *Count*: Repetitions, pages, or sets.
     - *Numeric Target*: Custom target (e.g., 2500 ml water).
   - **Frequency**:
     - *Daily*: Every calendar day.
     - *Weekdays*: Monday through Friday (weekends will not count against streaks).
     - *Weekends*: Saturday and Sunday only.
     - *Custom Days*: Select any combination of days (Mon-Sun).
   - **Start Date**: Date when tracking begins.
3. Click **Create Habit**.

### Preserving Historical Data on Target Changes
When editing a habit's target (e.g. increasing reading from 20 to 30 pages), DayBalance **does not rewrite historical entries**. Past daily records preserve their original target at logging time (`target_at_entry`), ensuring your historical completion metrics remain 100% accurate.

---

## 3. Daily Check-in Workflow (< 2 Minutes)

1. Open **Daily Check-in**.
2. Confirm the selected date (defaults to today).
3. In the **Scheduled Habits** tab:
   - Select status: `✓ Completed`, `◑ Partial`, `☕ Rest Day`, or `↷ Skipped`.
   - Enter numeric amounts if applicable.
   - Provide an optional skip reason or reflection.
   - Click **Save Habit Entries**.
4. In the **Lifestyle & Well-being** tab:
   - Record your sleep duration (e.g., 7.5 hrs) and quality (1-5).
   - Enter study minutes and number of focus blocks.
   - Enter exercise minutes and activity type.
   - Record subjective Mood (1-5) and Energy (1-5).
   - Click **Save Lifestyle Metrics**.

---

## 4. Understanding Streaks & Recovery

- **Unscheduled Days**: If a habit is scheduled only on weekdays, Saturday and Sunday **do not break your streak**.
- **Rest Days**: Marking an entry as `☕ Rest Day` preserves your active streak without counting as a missed day.
- **Grace Period**: If today is not yet logged, your active streak from yesterday is preserved and marked as pending.

---

## 5. Statistical Correlation Modeling

1. Navigate to **Analytics & Insights** ➔ Select **🔬 Statistical Correlation Explorer**.
2. Select two variables (e.g., *Sleep Duration* vs *Study / Focus Time*).
3. The engine computes:
   - **Pearson correlation ($r$)**: Linear relationship strength.
   - **Spearman rank correlation ($\rho$)**: Monotonic rank agreement.
   - **Sample size ($n$)**: Number of valid paired observations.
4. Read the plain-language interpretation and the scientific limitation disclaimer.

---

## 6. Running a Lifestyle Experiment (A/B Testing)

1. Navigate to **Goals & Experiments** ➔ **+ Launch New Experiment**.
2. Define a hypothesis:
   - *Example*: "Adding 15 minutes of morning meditation will increase afternoon study time."
3. Select the primary metric (*Study Time*).
4. Set sequential dates:
   - Baseline Period (e.g., Oct 1 to Oct 14).
   - Intervention Period (e.g., Oct 15 to Oct 28).
5. Open the **Habit Experiments** tab to review the automated comparison (means, standard deviations, difference, and percentage delta).

---

## 7. Using the Focus Timer

1. Open **Focus Timer**.
2. Enter your current task and select an associated study habit.
3. Choose a duration preset (25m Pomodoro, 45m block, 60m block, or Custom).
4. Click **Start / Resume**.
5. Once finished, click **Finish & Save**. The completed duration is automatically added to today's study records in SQLite.
