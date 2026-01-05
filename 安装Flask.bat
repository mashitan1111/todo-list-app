@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Installing Flask

echo ========================================
echo   Installing Flask
echo ========================================
echo.

python -m pip install flask
if errorlevel 1 (
    echo.
    echo Error: Failed to install Flask
    echo Please check your Python installation
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Flask installed successfully!
echo ========================================
echo.
pause
