# Vercel 部署完整指南

## ✅ 已完成的配置

1. ✅ 更新了 `settings.json` 添加 GitHub MCP 配置
2. ✅ 创建了 `vercel.json` 配置文件
3. ✅ 创建了 `requirements.txt` 依赖文件
4. ✅ 创建了 `.gitignore` 文件
5. ✅ 调整了 Flask 应用以适配 Vercel
6. ✅ 创建了 Vercel 入口文件 `api/index.py`
7. ✅ 调整了数据库路径以支持 Vercel 环境

## 🚀 部署步骤

### 步骤1：重启 Cursor

配置了 GitHub MCP 后，需要**完全重启 Cursor** 才能生效。

### 步骤2：准备 GitHub 仓库

你可以选择：
- **选项A**：让我通过 GitHub MCP 自动创建仓库
- **选项B**：手动创建 GitHub 仓库

如果选择选项A，请告诉我：
- 你的 GitHub 用户名
- 仓库名称（例如：`todo-list-app`）

### 步骤3：提交代码到 GitHub

如果选择手动方式：

```bash
cd "C:\Users\温柔的男子啊\Desktop\crusor\圆心工作\工具和脚本\工具脚本"
git init
git add .
git commit -m "Initial commit: Todo List App for Vercel"
git branch -M main
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

### 步骤4：在 Vercel 部署

1. 访问 [vercel.com](https://vercel.com)
2. 使用 GitHub 账号登录
3. 点击 "Add New Project"
4. 选择你的 GitHub 仓库
5. Vercel 会自动检测配置：
   - Framework Preset: Other
   - Root Directory: `工具和脚本/工具脚本`（或留空）
   - Build Command: （留空，Vercel 自动处理）
   - Output Directory: （留空）
6. 点击 "Deploy"

### 步骤5：配置环境变量（如需要）

在 Vercel 项目设置中，可以添加环境变量：
- `VERCEL=1`（已自动设置）

## 📁 项目结构

```
工具和脚本/工具脚本/
├── api/
│   └── index.py                    # Vercel入口文件
├── 工作待办清单桌面应用_精美版.py  # Flask应用主文件
├── database.py                    # 数据库模块
├── migrate_to_database.py         # 数据迁移脚本
├── vercel.json                   # Vercel配置文件
├── requirements.txt              # Python依赖
├── .gitignore                    # Git忽略文件
└── README_部署说明.md            # 部署说明
```

## ⚠️ 重要注意事项

### 1. 数据库存储

**Vercel 使用无服务器函数，文件系统是临时的！**

- SQLite 数据库文件存储在 `/tmp` 目录
- **每次函数调用后数据可能丢失**
- **建议使用外部数据库服务**：
  - Supabase (PostgreSQL) - 免费
  - PlanetScale (MySQL) - 免费
  - MongoDB Atlas - 免费
  - Railway (PostgreSQL) - 免费额度

### 2. 文件路径

- 应用已自动检测 Vercel 环境
- 数据库路径会自动切换到 `/tmp`
- Markdown 文件路径需要调整（如果使用）

### 3. 性能优化

- Vercel 无服务器函数有冷启动时间
- 首次访问可能需要几秒钟
- 后续访问会更快（函数保持热状态）

## 🔧 后续优化建议

### 1. 使用外部数据库

推荐使用 Supabase（免费 PostgreSQL）：

```python
# 安装依赖
# pip install supabase

# 在 database.py 中添加 Supabase 支持
```

### 2. 环境变量配置

在 Vercel 项目设置中添加：
- `DATABASE_URL` - 数据库连接字符串
- `SUPABASE_URL` - Supabase 项目 URL
- `SUPABASE_KEY` - Supabase API 密钥

### 3. 自定义域名

在 Vercel 项目设置中添加自定义域名

## 🐛 故障排除

### 问题1：导入错误

**错误**: `ModuleNotFoundError`

**解决**:
- 检查 `requirements.txt` 是否包含所有依赖
- 确保 Python 版本兼容（3.9+）

### 问题2：路由404

**错误**: 访问页面返回 404

**解决**:
- 检查 `vercel.json` 配置
- 确保 `api/index.py` 正确导出 `handler`

### 问题3：数据库错误

**错误**: 数据库文件找不到

**解决**:
- 检查数据库路径配置
- 考虑使用外部数据库服务

## 📞 需要帮助？

如果遇到问题：
1. 查看 Vercel 部署日志
2. 检查函数日志输出
3. 验证环境变量配置

## 🎉 部署成功后

访问你的 Vercel URL，例如：
- `https://your-project.vercel.app`

应用应该可以正常访问了！

---

**下一步**：告诉我你的 GitHub 用户名和仓库名称，我可以帮你自动创建仓库并提交代码！


