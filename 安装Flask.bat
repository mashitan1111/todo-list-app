@echo off
REM Set UTF-8 encoding first
chcp 65001 >nul 2>&1
title Install Flask

echo ========================================
echo   Install Flask Library
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
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo   Error: Python not found
    echo   Please install Python: https://www.python.org/
    echo ========================================
    pause
    exit /b 1
)

echo Checking Python version...
python --version
echo.

echo Checking pip version...
python -m pip --version
echo.

echo Installing Flask library...
echo This may take a few minutes, please wait...
echo.

REM Try using mirror source first
python -m pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo Mirror source failed, trying official source...
    python -m pip install flask
    if errorlevel 1 (
        echo.
        echo ========================================
        echo   Error: Flask installation failed
        echo.
        echo   Possible reasons:
        echo   1. Network connection problem
        echo   2. Firewall/proxy settings
        echo   3. pip configuration problem
        echo.
        echo   Solutions:
        echo   1. Check network connection
        echo   2. Run manually: pip install flask
        echo   3. Or use mirror: pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple
        echo ========================================
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Flask installed successfully!
echo ========================================
echo.
echo Verifying installation...
python -c "import flask; print('Flask version:', flask.__version__)"
if errorlevel 1 (
    echo Warning: Flask installed but cannot be imported, please check Python environment
) else (
    echo.
    echo You can now run "start_todo_app.bat"
)
echo.
pause
