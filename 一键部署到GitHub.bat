@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Deploy to GitHub

echo ========================================
echo   GitHub 自动部署
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check requests module
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Installing requests module...
    python -m pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 (
        echo Failed to install requests, trying official source...
        python -m pip install requests
    )
)

echo.
echo Starting deployment...
echo.

python deploy_to_github.py

echo.
pause

