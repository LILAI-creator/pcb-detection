@echo off
setlocal enabledelayedexpansion
title PCB Selenium Test (Edge)

set "BACKEND_DIR=%~dp0backend"
set "SELENIUM_DIR=%~dp0Selenium_tests"
set "HOST=0.0.0.0"
set "PORT=8000"
set "PYTHON_EXE=C:\Users\%USERNAME%\.conda\envs\yolo\python.exe"

echo.
echo  ============================================
echo     PCB Selenium Test - Edge Browser
echo  ============================================
echo.

echo  [1/6] Checking Python...
if not exist "%PYTHON_EXE%" (
    echo  [ERROR] Not found: %PYTHON_EXE%
    goto :fail
)
echo  [OK] %PYTHON_EXE%

echo  [2/6] Installing dependencies...
"%PYTHON_EXE%" -m pip install pytest selenium -q 2>nul
echo  [OK] Dependencies ready.

echo  [3/6] Checking port %PORT%...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    echo  [INFO] Killing process %%p on port %PORT%...
    taskkill /PID %%p /F >nul 2>&1
    ping -n 2 127.0.0.1 >nul
)

echo  [4/6] Starting backend server...
cd /d "%BACKEND_DIR%"
start /b "" "%PYTHON_EXE%" -m uvicorn app.main:app --host %HOST% --port %PORT% >nul 2>&1

echo  [INFO] Waiting for server ready...
set "READY=0"
for /l %%i in (1,1,30) do (
    if "!READY!"=="0" (
        "%PYTHON_EXE%" -c "import urllib.request; urllib.request.urlopen('http://localhost:%PORT%/docs', timeout=2)" >nul 2>&1
        if !errorlevel! equ 0 (
            set "READY=1"
            echo  [OK] Server ready.
        ) else (
            ping -n 2 127.0.0.1 >nul
        )
    )
)
if "!READY!"=="0" (
    echo  [ERROR] Server failed to start within 30s.
    goto :cleanup
)

echo  [5/6] Checking Edge WebDriver...
"%PYTHON_EXE%" -c "from selenium import webdriver; from selenium.webdriver.edge.service import Service; print('OK')" >nul 2>&1
if !errorlevel! neq 0 (
    echo  [ERROR] Selenium or Edge WebDriver not available.
    goto :cleanup
)
echo  [OK] Edge WebDriver ready.

echo  [6/6] Running Selenium tests...
echo.
cd /d "%SELENIUM_DIR%"
"%PYTHON_EXE%" -m pytest -v --tb=short
set "TEST_RESULT=!errorlevel!"

echo.
if !TEST_RESULT! equ 0 (
    echo  ============================================
    echo   Result: ALL TESTS PASSED
    echo  ============================================
) else (
    echo  ============================================
    echo   Result: SOME TESTS FAILED ^(exit code: !TEST_RESULT!^)
    echo  ============================================
)

:cleanup
echo.
echo  [INFO] Stopping backend server...
for /f "tokens=5" %%p in ('netstat -ano 2^>nul ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    taskkill /PID %%p /F >nul 2>&1
)
echo  [OK] Server stopped.

:fail
echo.
echo  Press any key to exit...
pause >nul
endlocal
