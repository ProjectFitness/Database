@echo off
rem One-time setup: creates a virtualenv, installs dependencies, fires a test
rem alert so you know the toast/sound/browser chain works before a real drop.
cd /d %~dp0
where python >nul 2>nul
if errorlevel 1 (
    echo Python not found. Install it from https://python.org and re-run.
    pause
    exit /b 1
)
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt
echo.
echo Setup done — firing a TEST alert now. You should hear a sound, see a
echo toast, and get a browser tab. If not, check Windows notification settings.
python -m monitor --test
pause
