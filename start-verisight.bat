@echo off
setlocal enabledelayedexpansion

title VeriSight Forensics Platform Launcher

echo ======================================================================
echo       VERISIGHT // DIGITAL SCREENSHOT FORENSICS ^& INTEGRITY WORKBENCH
echo              HackStellar 2026 - Problem Statement 12
echo ======================================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in PATH. Please install Python 3.11+.
    pause
    exit /b 1
)

:: 2. Check Node
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] npm was not found in PATH. Please install Node.js 18+.
    pause
    exit /b 1
)

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set FRONTEND_DIR=%SCRIPT_DIR%frontend

:: Auto-detect virtualenv if available
set "PYTHON_EXE=python"
if exist "%SCRIPT_DIR%backend\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%backend\.venv\Scripts\python.exe"
) else if exist "%SCRIPT_DIR%..\verisight\backend\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%..\verisight\backend\.venv\Scripts\python.exe"
) else if exist "%SCRIPT_DIR%..\verisight-hackstellar-ps12\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%..\verisight-hackstellar-ps12\.venv\Scripts\python.exe"
)

echo [1/4] Ensuring Golden Demo Samples are generated...
"%PYTHON_EXE%" "%SCRIPT_DIR%samples\generator.py"

echo [2/4] Starting FastAPI Forensic Core on http://127.0.0.1:8000...
start "VeriSight-Backend" cmd /k "cd /d "%BACKEND_DIR%" && "%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo [3/4] Starting Vite Workbench Frontend on http://localhost:5174...
start "VeriSight-Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm run dev"

echo [4/4] Opening Digital Forensics Workbench in default browser...
timeout /t 3 /nobreak >nul 2>nul
start http://localhost:5174

echo.
echo ======================================================================
echo  VeriSight Forensics Workbench is RUNNING!
echo  - Desktop UI:  http://localhost:5174
echo  - Backend API: http://127.0.0.1:8000/docs
echo  - Mobile Sync: Scan the QR code in the top command bar
echo ======================================================================
echo Close the backend and frontend terminal windows to stop the servers.
echo.
pause
