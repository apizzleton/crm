@echo off
REM Batch file to start the CRM app with keep-alive monitor
REM This ensures the app stays running and restarts automatically if it crashes
cd /d "%~dp0"
echo Starting CRM application with keep-alive monitor...
python keep_alive.py
pause















