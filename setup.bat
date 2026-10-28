@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo   DayBalance - Behavioral Habit and Consistency Intelligence
echo   Environment Setup & Installation Script
echo   90 Days - 90 Projects Challenge: Day 11
echo =====================================================================
echo.

cd /d "%~dp0"

:: 1. Verify Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in PATH.
    echo Please install Python 3.10+ from https://www.python.org/ and ensure
    echo "Add Python to PATH" is checked during installation.
    pause
    exit /b 1
)

echo [OK] Python runtime detected:
python --version
echo.

:: 2. Set up virtual environment
if not exist .venv (
    echo [INFO] Creating Python virtual environment in .venv...
    py -m venv .venv
    if %errorlevel% neq 0 (
        python -m venv .venv
    )
) else (
    echo [OK] Virtual environment .venv already exists.
)

:: 3. Verify and activate virtual environment
if exist .\.venv\Scripts\activate.bat (
    call .\.venv\Scripts\activate.bat
) else (
    echo [ERROR] Could not find virtual environment activation script in .venv.
    pause
    exit /b 1
)

echo.
echo [INFO] Installing required dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install required dependencies.
    pause
    exit /b %errorlevel%
)
echo [OK] All dependencies successfully installed.
echo.

:: 4. Ensure data directories exist
if not exist data mkdir data
if not exist data\exports mkdir data\exports
if not exist data\backups mkdir data\backups

:: 5. Initialize SQLite database & seed demo profile if needed
echo [INFO] Initializing SQLite database and pre-seeding demo dataset...
python -c "from services.demo_data_service import seed_demo_profile; seed_demo_profile(); print('[OK] Database initialized at data/daybalance.db')"
echo.

:: 6. Run verification tests
echo [INFO] Running test suite to verify installation health...
python -m pytest tests/ -v
if %errorlevel% neq 0 (
    echo [WARNING] Some tests reported issues. Please review output above.
) else (
    echo [PASS] All 26 automated tests passed successfully!
)

echo.
echo =====================================================================
echo   Setup Complete!
echo   Run the application using: run.bat
echo   Run test suite using:      test.bat
echo =====================================================================
pause
