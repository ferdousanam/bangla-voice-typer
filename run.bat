@echo off
title Bangla Voice Typer
cd /d "%~dp0"

echo [1/3] Checking virtual environment (.venv)...
set "VENV_OK=0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import PyQt6, pyaudio" >nul 2>&1
    if not errorlevel 1 (
        set "VENV_OK=1"
    )
)

if "%VENV_OK%"=="0" (
    echo Setting up virtual environment...
    if exist ".venv" rmdir /s /q ".venv"
    
    REM Prefer Python 3.12 or 3.13 where PyAudio binary wheels exist
    py -3.12 -m venv .venv >nul 2>&1
    if errorlevel 1 (
        py -3.13 -m venv .venv >nul 2>&1
    )
    if errorlevel 1 (
        python -m venv .venv
    )
    if errorlevel 1 (
        echo [Error] Python 3.12/3.13 or compatible Python was not found!
        pause
        exit /b 1
    )

    echo [2/3] Installing dependencies in .venv...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
) else (
    echo [2/3] Environment verified.
)

echo [3/3] Starting Bangla Voice Typer...
".venv\Scripts\python.exe" main.py

if errorlevel 1 (
    echo.
    echo [Error] Application encountered an issue.
    pause
)
