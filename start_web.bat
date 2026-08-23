@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m uvicorn app.api.server:app --host 127.0.0.1 --port 8000
) else (
    python run_web.py
)
pause
