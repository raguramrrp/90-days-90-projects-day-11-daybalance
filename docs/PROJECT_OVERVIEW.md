# DayBalance: Project Overview & Problem Space

**Day 11 — 90 Days : 90 Projects Challenge**  
**Author:** Ragu Ram P (Final-Year B.Tech Artificial Intelligence & Data Science)

---

## 1. Executive Summary

**DayBalance** is a local-first, privacy-conscious **Behavioral Habit Analytics & Consistency Intelligence Dashboard**. Unlike superficial habit trackers that focus exclusively on gamified "checkboxes" or punitive streak counters, DayBalance treats everyday personal behavior as an empirical data science problem.

The platform provides a calm, high-density analytical workspace where users can:
- Track habits with flexible frequencies (daily, weekdays, weekends, custom days).
- Record subjective and objective lifestyle metrics (sleep duration, sleep quality, focused study minutes, exercise duration, mood, and energy).
- Uncover genuine statistical relationships (Pearson and Spearman rank correlations) between sleep, movement, and cognitive output.
- Run structured personal A/B lifestyle experiments.
- Protect personal privacy with a 100% offline SQLite architecture.

---

## 2. Problem Statement & Motivation

1. **Gamification Fatigue & Shame-Based Abandonment**: Most commercial habit apps rely on rigid streaks. If a student falls sick or takes a scheduled recovery day, the app resets their counter to zero, causing emotional demoralization and eventual app abandonment.
2. **Lack of Analytical Depth**: Existing tools tell you *if* you completed a habit, but fail to explain *why*. They fail to answer: *Does sleeping an extra 45 minutes increase afternoon study time? Are Tuesdays consistently more productive than Sundays?*
3. **Privacy Intrusion**: Many lifestyle apps store sensitive daily thoughts, mental health ratings, and sleep schedules on third-party cloud servers, often monetizing or exposing private user telemetry.
4. **Shallow AI Gimmicks**: Many modern tools integrate expensive external LLM APIs that hallucinate behavioral patterns without statistical backing.

---

## 3. Core Objectives

| Objective | Implementation Strategy |
| :--- | :--- |
| **Schedule-Aware Consistency** | Streaks account for frequency rules; unscheduled days and rest days do not break progress. |
| **Rigorous Statistical Modeling** | Bivariate Pearson ($r$) and Spearman ($\rho$) correlation with strict sample-size safeguards ($n \ge 7$). |
| **Deterministic Insights** | Rule-based heuristics derived from database logs, paired with honest non-causal interpretations. |
| **A/B Lifestyle Experiments** | Baseline vs intervention statistical comparisons for self-directed personal experiments. |
| **Local-First Privacy** | SQLite WAL-mode engine with zero cloud telemetry, paid APIs, or external data sync. |

---

## 4. MVP Boundary & Scope

### In-Scope (Implemented & Tested)
- 9 Dedicated sections: Dashboard, Daily Check-in, Habits & Routines, Calendar & History, Analytics & Insights, Goals & Experiments, Focus Timer, Reports & Data, Settings & Profiles.
- Local multi-profile isolation with cascading safety deletes.
- Light and Dark modes with custom Teal design system tokens.
- Complete JSON profile backup and restore with ID remapping.
- CSV habit and daily log export and validated import.
- Integrated Pomodoro focus timer with direct study log persistence.
- Pre-seeded 60-day realistic student demo persona ("Alex Morgan").

### Out-of-Scope (Deferred to Future Releases)
- Machine Learning Clustering (k-means): Intentionally deferred until user baseline reaches $\ge 90$ days to prevent overfitting on sparse student logs.
- Cloud synchronization (preserves 100% local privacy).
- Native mobile binary (operates as desktop web application via Streamlit).
