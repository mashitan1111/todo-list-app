# 工作待办清单应用 - PowerShell启动脚本
# 用途：在PowerShell中启动应用，自动处理conda环境

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  工作待办清单桌面应用 - 精美版" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查并激活conda环境
if (Get-Command conda -ErrorAction SilentlyContinue) {
    Write-Host "正在激活conda环境..." -ForegroundColor Yellow
    conda activate base
    Write-Host "已激活conda环境: base" -ForegroundColor Green
} else {
    Write-Host "未检测到conda，使用系统Python" -ForegroundColor Yellow
}
Write-Host ""

# 检查Python
Write-Host "正在检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host $pythonVersion -ForegroundColor Green
} catch {
    Write-Host "错误：未找到Python" -ForegroundColor Red
    Write-Host "请先安装Python: https://www.python.org/" -ForegroundColor Red
    pause
    exit 1
}
Write-Host ""

# 检查Flask
Write-Host "正在检查Flask库..." -ForegroundColor Yellow
try {
    $flaskVersion = python -c "import flask; print('Flask版本:', flask.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $flaskVersion -ForegroundColor Green
        Write-Host "Flask已安装" -ForegroundColor Green
    } else {
        throw "Flask未安装"
    }
} catch {
    Write-Host "Flask未安装，正在安装..." -ForegroundColor Yellow
    pip install flask
    if ($LASTEXITCODE -ne 0) {
        Write-Host "错误：Flask安装失败" -ForegroundColor Red
        Write-Host "请手动运行: pip install flask" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "Flask安装成功！" -ForegroundColor Green
}
Write-Host ""

# 切换到脚本目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# 启动应用
Write-Host "正在启动应用..." -ForegroundColor Yellow
Write-Host "浏览器将自动打开，请稍候..." -ForegroundColor Yellow
Write-Host ""

python "工作待办清单桌面应用_精美版.py"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "错误：无法启动应用" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "1. Flask库未正确安装" -ForegroundColor Yellow
    Write-Host "2. 端口5000已被占用" -ForegroundColor Yellow
    Write-Host "3. Python脚本存在错误" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "解决方案：" -ForegroundColor Yellow
    Write-Host "1. 手动安装Flask: pip install flask" -ForegroundColor Yellow
    Write-Host "2. 检查端口占用: netstat -ano | findstr :5000" -ForegroundColor Yellow
    Write-Host "3. 查看错误详情（上方信息）" -ForegroundColor Yellow
    pause
    exit 1
}

