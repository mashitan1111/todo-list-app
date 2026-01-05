@echo off
REM Set UTF-8 encoding first
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Migrate Data to Database

echo ========================================
echo   Migrate Data to Database
echo ========================================
echo.

REM Try to activate conda environment
if exist "%CONDA_PREFIX%\Scripts\activate.bat" (
    call "%CONDA_PREFIX%\Scripts\activate.bat" base
) else if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\anaconda3\Scripts\activate.bat" base
) else if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\miniconda3\Scripts\activate.bat" base
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Migrating tasks from Markdown to database...
echo This may take a few moments...
echo.

python migrate_to_database.py

if errorlevel 1 (
    echo.
    echo Error: Failed to migrate data
    pause
    exit /b 1
)

echo.
echo Migration completed!
echo.
pause

