@echo off
REM Set UTF-8 encoding first
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Todo App

echo ========================================
echo   Todo List Application
echo ========================================
echo.

REM Try to activate conda environment
echo Checking conda environment...
if exist "%CONDA_PREFIX%\Scripts\activate.bat" (
    call "%CONDA_PREFIX%\Scripts\activate.bat" base
    echo Conda environment activated: %CONDA_DEFAULT_ENV%
) else if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\anaconda3\Scripts\activate.bat" base
    echo Conda environment activated: base
) else if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\miniconda3\Scripts\activate.bat" base
    echo Conda environment activated: base
) else if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    call "C:\ProgramData\anaconda3\Scripts\activate.bat" base
    echo Conda environment activated: base
) else if exist "C:\ProgramData\miniconda3\Scripts\activate.bat" (
    call "C:\ProgramData\miniconda3\Scripts\activate.bat" base
    echo Conda environment activated: base
) else (
    echo Using system Python
)
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 goto :error_python

python --version
echo.

REM Check Flask
echo Checking Flask...
python -c "import flask; print('Flask version:', flask.__version__)" 2>nul
if errorlevel 1 (
    echo Flask not found in current Python environment
    echo Installing Flask...
    echo This may take a few minutes...
    echo.
    python -m pip install flask
    if errorlevel 1 (
        echo.
        echo ========================================
        echo   Error: Failed to install Flask
        echo   Please run: pip install flask
        echo   Or run: install_flask.bat
        echo ========================================
        pause
        exit /b 1
    )
    echo Flask installed successfully!
) else (
    echo Flask is installed
)
echo.

REM Run application
echo Starting application...
echo Browser will open automatically, please wait...
echo.
python "工作待办清单桌面应用_精美版.py"
if errorlevel 1 goto :error_flask

goto :end

:error_python
chcp 65001 >nul 2>&1
echo.
echo Error: Python is not installed or not in PATH
echo Please install Python from https://www.python.org/
echo.
echo ========================================
echo   Error: Python not found
echo   Please install Python from https://www.python.org/
echo ========================================
pause
exit /b 1

:error_flask
chcp 65001 >nul 2>&1
echo.
echo Error: Failed to start application
echo.
echo Possible reasons:
echo 1. Flask not installed correctly
echo 2. Port 5000 is already in use
echo 3. Python script has errors
echo.
echo Solutions:
echo 1. Install Flask: pip install flask
echo 2. Check port: netstat -ano ^| findstr :5000
echo 3. Check error details above
echo.
echo ========================================
echo   Error: Failed to start application
echo   Please check the reasons above
echo ========================================
pause
exit /b 1

:end
