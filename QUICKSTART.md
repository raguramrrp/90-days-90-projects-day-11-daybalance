# DayBalance: Quick Start Guide

Get up and running with **DayBalance** on Windows in under 2 minutes.

---

## Fast Automated Setup (Recommended)

1. **Clone or navigate** to the project directory:
   ```cmd
   cd "D:\90 days\90-days-90-projects-day-11-daybalance"
   ```

2. **Run setup**:
   Double-click `setup.bat` or run:
   ```cmd
   setup.bat
   ```
   *This automatically creates `.venv`, installs dependencies, pre-seeds the 60-day demo dataset, and runs verification tests.*

3. **Launch the application**:
   Double-click `run.bat` or run:
   ```cmd
   run.bat
   ```
   Open your browser at: **`http://localhost:8501`**

---

## Manual Setup via Windows PowerShell

If you prefer configuring your environment manually:

```powershell
# 1. Navigate to directory
cd "D:\90 days\90-days-90-projects-day-11-daybalance"

# 2. Create Python virtual environment
python -m venv .venv

# 3. Activate virtual environment
# If execution policy restricts scripts, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1

# 4. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Pre-seed demo database
python -c "from services.demo_data_service import seed_demo_profile; seed_demo_profile()"

# 6. Run automated test suite
python -m pytest tests/ -v

# 7. Start DayBalance
python -m streamlit run app.py
```

---

## Default Profiles Available Immediately

- **Alex Morgan (Demo - Student & Builder)**: Pre-seeded with 60 days of realistic daily entries, streaks, habit experiments, and lifestyle co-variation.
- **Add Your Own**: Head to **Settings & Profiles** ➔ **+ Create New Local Profile** to start fresh with a personal dataset.
