@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo   Starting OraCLI 10G SQL*Plus Terminal Shell...
echo ===================================================

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py %*
) else (
    python main.py %*
)

endlocal
