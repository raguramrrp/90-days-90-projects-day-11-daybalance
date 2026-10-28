# DayBalance: Data Architecture & Demo Dataset

---

## 1. Storage Location & Engine

- **Database Path**: `data/daybalance.db`
- **Engine**: SQLite 3 with Write-Ahead Logging (`WAL` mode)
- **Exports Directory**: `data/exports/`
- **Backups Directory**: `data/backups/`

---

## 2. Demo Persona & Synthetic Dataset Specification

To enable immediate exploration without manual entry, DayBalance provides a deterministic, pre-seeded 60-day profile for student persona **Alex Morgan** (`is_demo = 1`).

### Demo Data Characteristics
- **Date Span**: Past 60 calendar days up to the current date.
- **Habits Included**:
  1. *Deep Study & Problem Solving* (Target: 120 mins, daily)
  2. *Daily Movement & Workout* (Target: 30 mins, weekdays)
  3. *Mindful Breathing & Stillness* (Target: 15 mins, daily)
  4. *Read Technical / Non-fiction* (Target: 20 pages, daily)
  5. *Sleep Consistency* (Target: 7.5+ hours, daily)
  6. *Digital Sunset at 10 PM* (Target: 1 completion, daily)
- **Realistic Statistical Properties**:
  - Sleep is normally distributed around $\mu = 7.4$ hours ($\sigma = 0.75$).
  - Study duration exhibits realistic positive co-variation with sleep duration ($r \approx +0.55$).
  - Exercise days show higher average energy ($4.2/5$) compared to rest days ($3.0/5$).
  - An active 11-day streak is maintained up to the present date to demonstrate active streak calculations.
- **Seed Reproducibility**: Generated with `random.seed(42)` to ensure deterministic outputs across test suites.

---

## 3. Data Privacy Statement

All data stored in `data/daybalance.db` remains 100% local. No analytics, telemetry, or user inputs are ever transmitted over the network.
