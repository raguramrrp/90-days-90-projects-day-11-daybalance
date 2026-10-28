# DayBalance: Troubleshooting & Frequently Asked Questions

---

## 1. Windows Setup & Environment Issues

### Issue: "PowerShell execution policy blocks script execution (`Activate.ps1`)"
**Symptom**:
```powershell
.\.venv\Scripts\Activate.ps1 : File cannot be loaded because running scripts is disabled on this system.
```
**Resolution**:
Run PowerShell with process-scoped execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```
Alternatively, invoke Python directly through the virtual environment without activating:
```cmd
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Or simply double-click `run.bat`.

---

### Issue: "Port 8501 is already in use"
**Symptom**:
Streamlit fails to bind to port 8501 or opens on port 8502.
**Resolution**:
Launch DayBalance on a custom port:
```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8510
```

---

### Issue: "SQLite OperationalError: database is locked"
**Symptom**:
Concurrent writes cause a temporary lock exception.
**Resolution**:
DayBalance activates Write-Ahead Logging (`PRAGMA journal_mode = WAL;`) and a 30-second timeout on all database connections. If another external tool (e.g., DB Browser for SQLite) has an open uncommitted lock on `data/daybalance.db`, close that application and restart DayBalance.

---

## 2. Common Analytics & Data Questions

### "Why is the Statistical Correlation Explorer showing 'Insufficient Data'?"
DayBalance enforces a strict sample-size safety threshold ($n \ge 7$ paired observations). If you have logged only 3 or 4 days recording both variables, DayBalance prevents calculation to avoid misleading or spurious correlation coefficients. Continue logging your daily check-ins to unlock analysis.

### "Does a positive correlation mean sleep causes higher study time?"
**No.** Correlation reflects co-variation, not causation. A positive correlation ($r > 0$) indicates that higher sleep hours frequently coincided with higher study minutes in your recorded history. However, external factors (such as class schedules, exams, or weekend free time) may influence both variables simultaneously.

### "How do I reset or clear the sample demo data?"
Navigate to **Settings & Profiles** ➔ **Demo Dataset Tools** ➔ Click **Seed / Refresh Demo Profile**. To use a completely clean profile, open the **Multi-Profile Manager** tab and click **+ Create New Local Profile**.
