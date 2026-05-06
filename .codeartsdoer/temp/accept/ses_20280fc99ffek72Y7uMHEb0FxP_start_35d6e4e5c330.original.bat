@echo off
chcp 65001 >nul
title PCB缺陷检测系统

echo ============================================
echo       PCB 缺陷检测系统 - 一键启动
echo ============================================
echo.

:: 检查 conda 是否可用
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 conda，请先安装 Anaconda 或 Miniconda
    pause
    exit /b 1
)

:: 激活 yolo 环境
echo [1/3] 激活 conda 环境: yolo
call conda activate yolo
if %errorlevel% neq 0 (
    echo [错误] conda 环境 'yolo' 不存在，正在创建...
    call conda create -n yolo python=3.9 -y
    call conda activate yolo
)

:: 启动服务
echo [3/3] 启动 FastAPI 服务...
echo.
echo ============================================
echo   访问地址: http://localhost:8000
echo   API文档:  http://localhost:8000/docs
echo   按 Ctrl+C 停止服务
echo ============================================
echo.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
