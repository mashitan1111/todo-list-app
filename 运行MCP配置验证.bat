@echo off
chcp 65001 >nul
cd /d "%~dp0"
python "MCP配置验证脚本.py"
pause

