@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 提交 Vercel 修复到 GitHub
echo ========================================
echo.

echo [1/3] 检查 Git 状态...
git status
echo.

echo [2/3] 添加所有修改的文件...
git add .
if %ERRORLEVEL% NEQ 0 (
    echo ✗ 添加文件失败
    pause
    exit /b 1
)
echo ✓ 文件已添加
echo.

echo [3/3] 提交并推送到 GitHub...
git commit -m "Fix Vercel deployment: encoding, paths, and dependencies"
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️ 提交失败（可能没有新更改）
) else (
    echo ✓ 代码已提交
)

echo.
echo 推送到 GitHub...
git push
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✓ 推送成功！
    echo ========================================
    echo.
    echo Vercel 会自动检测到新提交并重新部署
    echo 请等待 1-2 分钟后访问你的 Vercel URL
    echo.
) else (
    echo.
    echo ========================================
    echo ✗ 推送失败
    echo ========================================
    echo.
    echo 请检查：
    echo 1. GitHub Token 是否已设置
    echo 2. 网络连接是否正常
    echo 3. 远程仓库是否正确配置
    echo.
)

pause

