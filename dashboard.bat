@echo off
rem Opens the visual dashboard in your browser. Safe to run while the monitor
rem is running (it only reads the data files). Leave this window open.
cd /d %~dp0
set PY=python
if exist .venv\Scripts\python.exe set PY=.venv\Scripts\python.exe
%PY% -m monitor.dashboard
pause
