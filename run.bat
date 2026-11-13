@echo off
title Bangla Voice Typer
cd /d "%~dp0"

echo [1/3] Checking virtual environment (.venv)...
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [Error] Python was not found or failed to create .venv!
        pause
        exit /b 1
    )
)

echo [2/3] Checking dependencies in .venv...
".venv\Scripts\pip.exe" install -r requirements.txt --quiet

echo [3/3] Starting Bangla Voice Typer...
".venv\Scripts\python.exe" main.py

if errorlevel 1 (
    echo.
    echo [Error] Application encountered an issue.
    pause
)
