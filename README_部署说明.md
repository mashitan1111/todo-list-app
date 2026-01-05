# 工作待办清单应用 - Vercel 部署说明

## 🚀 快速部署到 Vercel

### 方法1：通过 GitHub 自动部署（推荐）

1. **将代码推送到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Todo List App"
   git remote add origin https://github.com/你的用户名/仓库名.git
   git push -u origin main
   ```

2. **在 Vercel 部署**
   - 访问 [vercel.com](https://vercel.com)
   - 点击 "New Project"
   - 导入你的 GitHub 仓库
   - Vercel 会自动检测 Python 项目并配置
   - 点击 "Deploy"

3. **配置环境变量（如需要）**
   - 在 Vercel 项目设置中添加环境变量
   - 数据库路径等配置会自动处理

### 方法2：使用 Vercel CLI

1. **安装 Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **登录 Vercel**
   ```bash
   vercel login
   ```

3. **部署**
   ```bash
   cd "工具和脚本/工具脚本"
   vercel
   ```

## 📁 项目结构

```
工具和脚本/工具脚本/
├── 工作待办清单桌面应用_精美版.py  # Flask应用主文件
├── database.py                    # 数据库模块
├── migrate_to_database.py         # 数据迁移脚本
├── vercel.json                   # Vercel配置文件
├── requirements.txt              # Python依赖
└── .gitignore                    # Git忽略文件
```

## ⚙️ Vercel 配置说明

### vercel.json
- 使用 `@vercel/python` 构建器
- 所有路由指向 Flask 应用
- Python 版本：3.9

### requirements.txt
- Flask 2.3.3
- Werkzeug 2.3.7

## 🔧 注意事项

1. **数据库文件**
   - SQLite 数据库文件需要存储在 Vercel 的文件系统中
   - 建议使用环境变量配置数据库路径
   - 或者使用外部数据库服务（如 Supabase、PlanetScale）

2. **文件路径**
   - Vercel 使用无服务器环境
   - 文件路径可能需要调整
   - 建议使用环境变量或 Vercel 存储

3. **数据持久化**
   - Vercel 的无服务器函数是临时性的
   - 数据库文件在每次部署时可能重置
   - 建议使用外部数据库服务

## 🌐 部署后访问

部署成功后，Vercel 会提供一个 URL，例如：
- `https://your-project.vercel.app`

## 📝 后续优化建议

1. **使用外部数据库**
   - Supabase (PostgreSQL)
   - PlanetScale (MySQL)
   - MongoDB Atlas

2. **环境变量配置**
   - 数据库连接字符串
   - API 密钥
   - 其他敏感信息

3. **自定义域名**
   - 在 Vercel 项目设置中添加自定义域名

## 🐛 故障排除

### 问题1：导入错误
- 确保所有依赖都在 `requirements.txt` 中
- 检查 Python 版本兼容性

### 问题2：数据库错误
- 检查文件路径是否正确
- 考虑使用外部数据库服务

### 问题3：路由错误
- 检查 `vercel.json` 配置
- 确保 Flask 应用正确导出

## 📞 技术支持

如有问题，请检查：
1. Vercel 部署日志
2. 应用日志输出
3. 环境变量配置


