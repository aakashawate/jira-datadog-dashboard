@echo off
echo ======================================================
echo          UNIFIED MONITORING DASHBOARD
echo ======================================================
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Start the dashboard server
echo Starting dashboard server...
python dashboard_server.py

pause
