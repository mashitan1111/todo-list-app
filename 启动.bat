@echo off
cd /d "%~dp0"
start "Todo App" cmd /k "cd /d ""%~dp0"" && python launch.py"
exit
