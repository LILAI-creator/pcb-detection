@echo off
title PCB Defect Detection

set "BACKEND_DIR=%~dp0backend"
set "HOST=0.0.0.0"
set "PORT=8000"
set "PYTHON_EXE=C:\Users\%USERNAME%\.conda\envs\yolo\python.exe"

echo.
echo  ============================================
echo       PCB Defect Detection System
echo  ============================================
echo.

echo  [1/5] Checking port %PORT%...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    echo  [INFO] Killing process %%p on port %PORT%...
    taskkill /PID %%p /F >nul 2>&1
    ping -n 2 127.0.0.1 >nul
)
echo  [OK] Port ready.

echo  [2/5] Finding Python...
if not exist "%PYTHON_EXE%" (
    echo  [ERROR] Not found: %PYTHON_EXE%
    goto :fail
)
echo  [OK] %PYTHON_EXE%

echo  [3/5] Installing dependencies...
"%PYTHON_EXE%" -m pip install -r "%BACKEND_DIR%\requirements.txt" -q 2>nul
echo  [OK] Dependencies ready.

echo  [4/5] Checking model...
if exist "%BACKEND_DIR%\weights\best.pt" (
    echo  [OK] Model: best.pt
    set "RUN_MODE=YOLOv8"
) else (
    echo  [WARN] No model, MOCK mode.
    set "RUN_MODE=MOCK"
)

echo  [5/5] Checking SQL Server...
"%PYTHON_EXE%" -c "import pyodbc; c=pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=pcb_detector;UID=sa;PWD=h4fFwT77dNQj;',timeout=5); c.close()" >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] SQL Server connected.
) else (
    echo  [WARN] SQL Server not connected.
)

echo.
echo  ============================================
echo   Mode : %RUN_MODE%
echo   URL  : http://localhost:%PORT%
echo   Login: http://localhost:%PORT%/login.html
echo   Docs : http://localhost:%PORT%/docs
echo  ============================================
echo.

cd /d "%BACKEND_DIR%"
"%PYTHON_EXE%" -m uvicorn app.main:app --host %HOST% --port %PORT% --reload

:fail
echo.
echo  Press any key to exit...
pause >nul
