@echo off
rem Keeps the monitor alive forever: if it ever crashes or the machine reboots
rem (schedule this file in Task Scheduler "At log on"), it relaunches in 5s.
cd /d %~dp0
set PY=python
if exist .venv\Scripts\python.exe set PY=.venv\Scripts\python.exe
:loop
%PY% -m monitor config.yaml
echo Monitor exited — restarting in 5 seconds (Ctrl+C twice to stop for real)
timeout /t 5 /nobreak >nul
goto loop
