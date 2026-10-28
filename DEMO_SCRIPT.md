# DayBalance: 90-Second Demonstration Script

Use this structured walkthrough for recruiter presentations, portfolio interviews, or video demonstrations.

---

## 1. Setup (0:00 - 0:10)
- **Action**: Launch application via `run.bat` or `python -m streamlit run app.py`.
- **Narration**: *"This is DayBalance, a local-first behavioral habit analytics and consistency intelligence platform built in Python, Streamlit, and SQLite for Day 11 of my 90 Days : 90 Projects challenge."*

---

## 2. Dashboard & Schedule-Aware Consistency (0:10 - 0:30)
- **Action**: Show the Dashboard overview with Alex Morgan's pre-seeded 60-day dataset. Point to the 4 metric cards and the habit schedule table.
- **Narration**: *"Unlike superficial trackers that only count checkboxes, DayBalance tracks flexible frequencies. If a habit is scheduled only on weekdays, weekends do not break your streak. Explicit rest days are protected, avoiding the shame-based abandonment common in gamified apps."*
- **Action**: Point to the Activity Heatmap and Weekday Consistency chart.
- **Narration**: *"The dashboard immediately reveals that consistency averages 84% on Tuesdays versus 52% on Sundays."*

---

## 3. Daily Check-in in Under 2 Minutes (0:30 - 0:45)
- **Action**: Navigate to **Daily Check-in**. Show today's habits with one-click status selection (`Completed`, `Partial`, `Rest Day`, `Skipped`). Switch to the **Lifestyle & Well-being** tab.
- **Narration**: *"The daily check-in takes under two minutes. Users can record sleep duration, study minutes, exercise, and subjective mood and energy ratings on clean 1-to-5 scales."*

---

## 4. Advanced Statistical Modeling & Differentiator (0:45 - 1:10)
- **Action**: Navigate to **Analytics & Insights** ➔ **🔬 Statistical Correlation Explorer**.
- **Action**: Select *Sleep Duration (Hours)* vs *Study / Focus Time (Minutes)*.
- **Narration**: *"This is the core portfolio differentiator: genuine bivariate relationship modeling. DayBalance calculates both Pearson correlation for linear co-variation and Spearman rank correlation for ordinal metrics like mood and sleep quality. Notice our sample-size guardrail: calculations require at least 7 paired days to prevent misleading spurious correlations. Crucially, every insight includes an explicit scientific reminder that correlation does not establish causation."*

---

## 5. Habit Experiments & Focus Timer (1:10 - 1:25)
- **Action**: Open **Goals & Experiments** and show the A/B comparison card.
- **Narration**: *"Users can formulate self-directed lifestyle experiments—for instance, evaluating how adding morning meditation changes afternoon focus blocks by comparing baseline vs intervention means and percentage deltas."*
- **Action**: Open **Focus Timer**, start a 25-minute Pomodoro, and show session saving.
- **Narration**: *"The built-in Pomodoro timer automatically persists completed deep work sessions directly into daily study records."*

---

## 6. Local Privacy & Data Portability (1:25 - 1:30)
- **Action**: Open **Reports & Data** and show JSON backup and CSV export. Toggle between Dark and Light mode.
- **Narration**: *"DayBalance operates 100% locally with zero cloud dependencies or paid APIs. It supports multi-profile isolation, full JSON snapshots, and refined Sage Green & Warm Ivory editorial wellness styling in both light and dark themes."*
