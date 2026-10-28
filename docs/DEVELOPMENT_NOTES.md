# DayBalance: Development Notes & Technical Decisions

---

## 1. Local-First Engineering Philosophy

- **Zero Cloud Leakage**: Personal behavioral logs, subjective mood ratings, and sleep schedules must never leave the user's local machine.
- **SQLite with WAL Mode**: We selected SQLite over flat JSON or CSV files because SQLite guarantees transactional atomicity (ACID), foreign-key referential integrity (`PRAGMA foreign_keys = ON;`), and high-performance concurrent reads via Write-Ahead Logging (`PRAGMA journal_mode = WAL;`).
- **No Paid APIs or Black-Box LLMs**: All behavioral insights are generated deterministically using transparent heuristics and standard numerical algorithms in NumPy and Pandas.

---

## 2. Streak Algorithm Implementation & Edge Cases

Traditional streak algorithms iterate backwards naively and break upon encountering any date without a checkmark. DayBalance addresses several critical real-world edge cases:

1. **Schedule-Awareness**:
   - Habits define a `frequency` and `frequency_days` (JSON list of integers 0–6).
   - The algorithm only inspects calendar dates matching the habit's defined schedule.
   - Example: A weekday-only habit evaluated on Monday checks Friday as the previous scheduled day, skipping Saturday and Sunday.

2. **Graceful Rest Days**:
   - When an entry has `status == 'rest_day'`, the backward scan continues without resetting the running count.

3. **Current vs Best Streak**:
   - `best_streak` is computed using a forward pass across all historical scheduled occurrences since `start_date`.
   - `current_streak` is computed using a backward pass from the evaluation date, accounting for whether today is currently pending.

---

## 3. Statistical Analysis Guardrails

- **Configurable Minimum Sample Size ($n \ge 7$)**:
  Evaluating correlations on small datasets ($n < 7$) produces high sampling error and spurious coefficients. DayBalance blocks calculation when $n < n_{min}$, guiding the user on how many additional days of paired data are required.
- **Zero Variance Handling**:
  If a user logs identical values for every day (e.g. sleep = 8.0h every single day), standard deviation is zero, which would cause a division-by-zero error in the Pearson denominator. The engine checks `std == 0` and returns a clear explanation.
- **Non-Causal Interpretations**:
  Every statistical card features an explicit limitation notice emphasizing that correlation does not establish causation.

---

## 4. UI Theme Tokens & Streamlit State Management

- Streamlit reruns the script on each user interaction. To ensure the interface feels responsive and visually cohesive:
  - Custom CSS variables (`--db-bg`, `--db-surface`, `--db-accent`) are injected dynamically according to the user's active theme selection (`dark` or `light`).
  - Plotly layout templates (`plotly_dark` and `plotly_white`) synchronize with CSS tokens.
  - Profile preferences persist to SQLite so that selected themes, quiet hours, and display settings remain saved across browser restarts.
