@echo off
chcp 65001 >nul
cd /d "%~dp0"
python "Agent启动检查验证脚本.py"
pause

