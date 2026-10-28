@echo off
setlocal

echo =====================================================================
echo   DayBalance - Behavioral Habit Analytics ^& Health Wearable Tracker
echo   Offline Local Desktop Application
echo   Day 11: 90 Days - 90 Projects Challenge
echo =====================================================================
echo.

cd /d "%~dp0"

:: Activate virtual environment if present
if exist .\.venv\Scripts\activate.bat (
    call .\.venv\Scripts\activate.bat
)

set PYTHONPATH=%~dp0

:: Launch native desktop application
if exist .\.venv\Scripts\python.exe (
    .\.venv\Scripts\python.exe app.py %*
) else (
    python app.py %*
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] DayBalance exited with error code %errorlevel%.
    pause
)
