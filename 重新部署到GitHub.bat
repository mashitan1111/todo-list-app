@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 重新部署到 GitHub（清理 Git 历史）
echo ========================================
echo.

echo [1/6] 删除本地 Git 历史...
if exist .git (
    rmdir /s /q .git
    echo ✓ Git 历史已删除
) else (
    echo ✓ 没有 Git 历史需要删除
)
echo.

echo [2/6] 初始化新的 Git 仓库...
git init
git branch -M main
echo ✓ Git 仓库已初始化
echo.

echo [3/6] 检查代码中的 Token 泄露...
python 检查Token泄露.py
if %ERRORLEVEL% NEQ 0 (
    echo ✗ 发现代码中包含硬编码的 Token，请先清理
    goto :error
)
echo ✓ 代码检查通过
echo.

echo [4/6] 添加所有文件...
git add .
echo ✓ 文件已添加
echo.

echo [5/6] 提交代码...
git commit -m "Initial commit: Todo List App for Vercel (clean version)"
echo ✓ 代码已提交
echo.

echo [6/6] 检查并创建 GitHub 仓库（如果不存在）...
if "%GITHUB_TOKEN%"=="" (
    echo ✗ 错误: GITHUB_TOKEN 环境变量未设置
    echo   请先运行: setx GITHUB_TOKEN "YOUR_TOKEN_HERE"
    echo   然后重新打开命令行窗口
    goto :error
)
python 创建GitHub仓库.py
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ 仓库创建失败，但继续尝试推送...
)
echo.

echo [7/7] 添加远程仓库并推送...
git remote add origin https://github.com/mashitan1111/todo-list-app.git 2>nul
git remote set-url origin https://github.com/mashitan1111/todo-list-app.git

REM 配置 Git 用户信息（如果未配置）
git config user.name "mashitan1111" 2>nul
git config user.email "994404569@qq.com" 2>nul

REM 使用 Token 推送（将 Token 嵌入 URL）
git remote set-url origin https://%GITHUB_TOKEN%@github.com/mashitan1111/todo-list-app.git

REM 使用 Python 脚本推送并记录日志
python 推送并记录日志.py
set PUSH_RESULT=%ERRORLEVEL%

if %PUSH_RESULT% EQU 0 (
    echo ✓ 推送成功！
) else (
    echo.
    echo ⚠️ 推送失败，尝试使用标准方式...
    REM 恢复标准 URL
    git remote set-url origin https://github.com/mashitan1111/todo-list-app.git
    REM 使用 Git Credential Manager
    echo https://%GITHUB_TOKEN%@github.com | git credential approve
    git push -u origin main --force
    set PUSH_RESULT=%ERRORLEVEL%
)
echo.

if %PUSH_RESULT% EQU 0 (
    echo ========================================
    echo ✓ 部署成功！
    echo ========================================
    echo.
    echo 你的应用已部署到：
    echo https://github.com/mashitan1111/todo-list-app
    echo.
) else (
    echo ========================================
    echo ✗ 推送失败
    echo ========================================
    echo.
    echo 请检查：
    echo 1. GitHub Token 是否已设置为环境变量 GITHUB_TOKEN
    echo 2. 网络连接是否正常
    echo 3. 远程仓库是否存在
    echo.
    echo 如果远程仓库不存在，请先访问：
    echo https://github.com/new
    echo 创建名为 todo-list-app 的仓库
    echo.
)

:error
pause

