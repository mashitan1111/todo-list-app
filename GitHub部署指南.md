# GitHub 部署完整指南

## 📋 前置准备

1. **GitHub 账号信息**
   - 用户名：`mashitan1111`
   - 邮箱：`994404569@qq.com`
   - Token：已配置在 settings.json

2. **需要安装的软件**
   - Git（如果未安装）：https://git-scm.com/download/win
   - Python（已安装）

## 🚀 方法1：使用批处理文件自动部署（推荐）

### 步骤1：双击运行批处理文件

直接双击运行：
```
一键部署到GitHub.bat
```

脚本会自动：
1. 检查并安装 requests 库
2. 创建 GitHub 仓库
3. 初始化 Git 仓库
4. 提交所有文件
5. 推送到 GitHub

### 如果遇到问题

如果批处理文件运行失败，请使用方法2手动部署。

---

## 🛠️ 方法2：手动部署（最可靠）

### 步骤1：打开命令提示符（CMD）

1. 按 `Win + R`
2. 输入 `cmd` 并回车
3. 切换到项目目录：
```cmd
cd /d "C:\Users\温柔的男子啊\Desktop\crusor\圆心工作\工具和脚本\工具脚本"
```

### 步骤2：安装 requests 库（如果未安装）

```cmd
python -m pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤3：运行部署脚本

```cmd
python deploy_to_github.py
```

脚本会自动完成：
- ✅ 创建 GitHub 仓库 `todo-list-app`
- ✅ 初始化 Git
- ✅ 提交代码
- ✅ 推送到 GitHub

### 步骤4：如果脚本失败，手动执行 Git 命令

如果自动脚本失败，可以手动执行：

```cmd
REM 1. 初始化 Git（如果还没有）
git init

REM 2. 配置 Git 用户信息
git config user.name "mashitan1111"
git config user.email "994404569@qq.com"

REM 3. 添加所有文件
git add .

REM 4. 提交
git commit -m "Initial commit: Todo List App for Vercel"

REM 5. 添加远程仓库（需要先在 GitHub 网页创建仓库）
git remote add origin https://github.com/mashitan1111/todo-list-app.git

REM 6. 推送到 GitHub
git branch -M main
git push -u origin main
```

**注意**：如果使用 Token 推送，需要先设置环境变量：
```cmd
set GITHUB_TOKEN=your_token_here
```
然后 URL 格式为：
```
https://your_token_here@github.com/mashitan1111/todo-list-app.git
```

---

## 🌐 方法3：在 GitHub 网页创建仓库

### 步骤1：访问 GitHub

1. 打开浏览器，访问：https://github.com/new
2. 登录你的账号 `mashitan1111`

### 步骤2：创建新仓库

1. **Repository name**: `todo-list-app`
2. **Description**: `工作待办清单应用 - Flask Web Application`
3. **Visibility**: 选择 `Public`（公开）或 `Private`（私有）
4. **不要**勾选 "Initialize this repository with a README"
5. 点击 **"Create repository"**

### 步骤3：在本地执行 Git 命令

在项目目录打开 CMD，执行：

```cmd
cd /d "C:\Users\温柔的男子啊\Desktop\crusor\圆心工作\工具和脚本\工具脚本"

REM 设置 GitHub Token 环境变量（替换为你的实际 token）
set GITHUB_TOKEN=your_token_here

git init
git config user.name "mashitan1111"
git config user.email "994404569@qq.com"
git add .
git commit -m "Initial commit: Todo List App for Vercel"
git branch -M main
git remote add origin https://%GITHUB_TOKEN%@github.com/mashitan1111/todo-list-app.git
git push -u origin main
```

---

## ✅ 验证部署

部署成功后，访问：
```
https://github.com/mashitan1111/todo-list-app
```

你应该能看到所有文件已经上传。

---

## 🚀 下一步：在 Vercel 部署

### 步骤1：访问 Vercel

1. 打开浏览器，访问：https://vercel.com
2. 使用 GitHub 账号登录

### 步骤2：导入项目

1. 点击 **"Add New Project"** 或 **"Import Project"**
2. 选择你的 GitHub 仓库 `mashitan1111/todo-list-app`
3. Vercel 会自动检测配置：
   - **Framework Preset**: Other
   - **Root Directory**: `工具和脚本/工具脚本`（或留空，如果文件在根目录）
   - **Build Command**: （留空）
   - **Output Directory**: （留空）
4. 点击 **"Deploy"**

### 步骤3：等待部署完成

Vercel 会自动：
- 安装依赖（从 requirements.txt）
- 构建项目
- 部署到全球 CDN

### 步骤4：访问你的应用

部署完成后，Vercel 会提供一个 URL，例如：
```
https://todo-list-app.vercel.app
```

---

## ⚠️ 重要提示

### 1. 数据库存储

Vercel 使用无服务器函数，SQLite 数据库存储在临时目录 `/tmp`，**数据不会持久化**。

**建议**：
- 使用外部数据库服务（Supabase、PlanetScale 等）
- 或使用 Vercel KV（键值存储）

### 2. 文件路径

应用已自动检测 Vercel 环境，数据库路径会自动切换到 `/tmp`。

### 3. 环境变量

如果需要配置环境变量，在 Vercel 项目设置中添加：
- `VERCEL=1`（已自动设置）

---

## 🐛 故障排除

### 问题1：Git 推送失败

**错误**: `remote: Support for password authentication was removed`

**解决**: 使用 Token 在 URL 中，或配置 Git Credential Manager

### 问题2：Vercel 部署失败

**错误**: `ModuleNotFoundError`

**解决**: 检查 `requirements.txt` 是否包含所有依赖

### 问题3：应用无法访问

**错误**: 404 或 500 错误

**解决**: 
1. 检查 Vercel 部署日志
2. 检查 `vercel.json` 配置
3. 确保 `api/index.py` 正确导出 `handler`

---

## 📞 需要帮助？

如果遇到问题：
1. 查看 GitHub 仓库：https://github.com/mashitan1111/todo-list-app
2. 查看 Vercel 部署日志
3. 检查应用日志输出

---

**祝你部署顺利！** 🎉

