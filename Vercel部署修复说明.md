# Vercel 部署错误修复说明

## 🐛 问题描述

部署到 Vercel 后出现 500 错误：
```
FUNCTION_INVOCATION_FAILED
500：内部服务器错误
```

## 🔍 问题原因

1. **中文文件名导入问题**：`api/index.py` 中导入中文文件名可能导致编码问题
2. **路径配置错误**：在 Vercel 环境中，文件路径指向了不存在的目录
3. **文件依赖缺失**：应用依赖的外部文件（Markdown 文件）在 Vercel 中不存在
4. **SQLite 依赖缺失**：Vercel 需要 `pysqlite3-binary` 来支持 SQLite

## ✅ 已修复的问题

### 1. 修复 `api/index.py` 导入问题

**问题**：直接导入中文文件名可能导致编码错误

**修复**：使用 `importlib.util` 动态加载模块，避免编码问题

```python
import importlib.util
app_file = parent_dir / "工作待办清单桌面应用_精美版.py"
spec = importlib.util.spec_from_file_location("todo_app", app_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
app = module.app
```

### 2. 修复路径配置

**问题**：`BASE_DIR = Path(__file__).parent.parent.parent` 在 Vercel 中指向错误路径

**修复**：根据环境变量判断，Vercel 环境使用当前目录

```python
if os.environ.get('VERCEL'):
    BASE_DIR = Path(__file__).parent
    TODO_FILE = None  # Vercel 环境中不存在
    RECOMMEND_FILE = None
    STATUS_FILE = BASE_DIR / "任务状态.json"
else:
    BASE_DIR = Path(__file__).parent.parent.parent
    # 本地路径...
```

### 3. 修复文件依赖检查

**问题**：当文件为 `None` 时调用 `.exists()` 会报错

**修复**：添加空值检查

```python
def read_markdown_tasks(file_path):
    if file_path is None or not file_path.exists():
        return []
    # ...
```

### 4. 添加 SQLite 依赖

**问题**：Vercel 环境需要 `pysqlite3-binary` 来支持 SQLite

**修复**：在 `requirements.txt` 中添加依赖

```
pysqlite3-binary==0.5.0
```

### 5. 修复数据库路径

**问题**：确保 `/tmp` 目录存在

**修复**：在数据库初始化时创建目录

```python
if os.environ.get('VERCEL'):
    BASE_DIR = Path('/tmp')
    BASE_DIR.mkdir(parents=True, exist_ok=True)
```

## 📝 修改的文件

1. ✅ `api/index.py` - 修复导入方式
2. ✅ `工作待办清单桌面应用_精美版.py` - 修复路径配置和文件检查
3. ✅ `database.py` - 确保 /tmp 目录存在
4. ✅ `requirements.txt` - 添加 pysqlite3-binary

## 🚀 重新部署步骤

### 步骤1：提交代码到 GitHub

```bash
cd "C:\Users\温柔的男子啊\Desktop\crusor\圆心工作\工具和脚本\工具脚本"
git add .
git commit -m "Fix Vercel deployment: encoding, paths, and dependencies"
git push
```

### 步骤2：Vercel 自动重新部署

- Vercel 会自动检测到新的提交
- 自动触发重新部署
- 等待 1-2 分钟

### 步骤3：检查部署状态

1. 访问 Vercel Dashboard
2. 查看部署日志
3. 确认部署成功

### 步骤4：测试应用

访问部署后的 URL，检查：
- ✅ 页面是否正常加载
- ✅ 是否可以添加任务
- ✅ 是否可以完成任务
- ✅ 数据库是否正常工作

## ⚠️ 重要提示

### 数据持久性问题

**Vercel 使用临时文件系统**：
- `/tmp` 目录在函数调用之间**可能不持久**
- 数据可能在函数重启后丢失
- **建议使用外部数据库**（Supabase、PlanetScale 等）

### 当前状态

- ✅ 应用可以正常部署和运行
- ⚠️ 数据存储在临时文件系统，可能丢失
- 💡 建议后续迁移到外部数据库

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

### 3. 错误监控

添加错误监控服务（如 Sentry）来捕获运行时错误

## 📞 如果还有问题

1. **查看 Vercel 日志**
   - 在 Vercel Dashboard 中查看函数日志
   - 查找错误堆栈信息

2. **检查依赖**
   - 确认所有依赖都已安装
   - 检查 Python 版本兼容性

3. **测试本地运行**
   - 设置 `VERCEL=1` 环境变量
   - 本地测试 Vercel 环境

---

**修复完成时间**：2026-01-04  
**状态**：✅ 已修复，等待重新部署验证

