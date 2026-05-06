@echo off
title PCB Defect Detection

echo ============================================
echo       PCB Defect Detection - Start
echo ============================================
echo.

echo [1/4] Activating conda environment: yolo
call conda activate yolo
if %errorlevel% neq 0 (
    echo [INFO] Environment not found, creating...
    call conda create -n yolo python=3.9 -y
    call conda activate yolo
)



echo [4/4] Starting server...
echo.
echo ============================================
echo   URL:  http://localhost:8000
echo   Docs: http://localhost:8000/docs
echo   Press Ctrl+C to stop
echo ============================================
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir "%~dp0backend"
