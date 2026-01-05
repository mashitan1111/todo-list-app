@echo off
chcp 65001 >nul
cd /d "%~dp0"
python "大文件分批写入工具.py"
pause

