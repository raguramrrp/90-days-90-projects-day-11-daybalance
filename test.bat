@echo off
setlocal

echo =====================================================================
echo   Running DayBalance Automated Test Suite (pytest)
echo   Streaks, Schedule-Awareness, Statistical Correlations, and Integrity
echo =====================================================================
echo.

cd /d "%~dp0"

if exist .\.venv\Scripts\activate.bat (
    call .\.venv\Scripts\activate.bat
)

set PYTHONPATH=%~dp0

if exist .\.venv\Scripts\pytest.exe (
    .\.venv\Scripts\pytest.exe tests/ -v
) else (
    python -m pytest tests/ -v
)

set TEST_EXIT_CODE=%errorlevel%

echo.
if %TEST_EXIT_CODE% equ 0 (
    echo [PASS] All automated tests passed successfully!
) else (
    echo [FAIL] Automated tests failed with exit code %TEST_EXIT_CODE%.
)

exit /b %TEST_EXIT_CODE%
