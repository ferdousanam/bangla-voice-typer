@echo off
setlocal
title Bangla Voice Typer - Portable Builder
cd /d "%~dp0"

echo ==========================================================
echo        Bangla Voice Typer - Portable Build Script
echo ==========================================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not found. Please install Python or setup .venv.
        pause
        exit /b 1
    )
    set "PYTHON_CMD=python"
)

echo Checking build dependencies...
%PYTHON_CMD% -m pip install --quiet pyinstaller

echo.
echo Starting portable build...
%PYTHON_CMD% build_portable.py

if %errorlevel% equ 0 (
    echo.
    echo ==========================================================
    echo [SUCCESS] Portable build completed successfully!
    echo Check the 'dist' directory for your portable release.
    echo ==========================================================
) else (
    echo.
    echo [ERROR] Build failed. Please check the logs above.
)

echo.
pause
