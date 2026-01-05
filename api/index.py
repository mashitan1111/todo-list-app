# Vercel无服务器函数入口
# 这个文件用于Vercel部署，将Flask应用作为无服务器函数运行

import sys
import os
from pathlib import Path

# 设置Vercel环境变量（必须在导入应用之前设置）
os.environ['VERCEL'] = '1'

# 添加父目录到路径，以便导入应用
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# 导入Flask应用
# 注意：使用 importlib 动态加载，因为文件名包含中文
import importlib.util
from flask import Flask

# 获取应用文件路径
app_file = parent_dir / "工作待办清单桌面应用_精美版.py"
if not app_file.exists():
    raise FileNotFoundError(f"Application file not found: {app_file}")

# 使用绝对路径字符串，确保编码正确
app_file_path = str(app_file.resolve())

# 动态加载模块
spec = importlib.util.spec_from_file_location("todo_app_module", app_file_path)
if spec is None or spec.loader is None:
    raise ImportError(f"Failed to create module spec for: {app_file_path}")

# 创建并执行模块
todo_module = importlib.util.module_from_spec(spec)
sys.modules['todo_app_module'] = todo_module

try:
    spec.loader.exec_module(todo_module)
except Exception as e:
    raise ImportError(f"Failed to execute module: {e}")

# 获取 Flask 应用实例
if not hasattr(todo_module, 'app'):
    raise AttributeError("Flask app 'app' not found in module")

# 获取 app 实例
flask_app = todo_module.app

# 验证 app 是 Flask 应用实例
if not isinstance(flask_app, Flask):
    raise TypeError(f"Expected Flask instance, got {type(flask_app)}: {flask_app}")

# 确保 app 对象有正确的类型信息
# Vercel 需要能够识别这是 Flask 应用
app = flask_app

# 显式设置 __class__ 属性，确保类型信息正确
# 这有助于 Vercel 正确识别 Flask 应用
if not hasattr(app, '__class__'):
    app.__class__ = Flask

# Vercel 会自动识别 Flask 应用并处理
# 直接导出 app 对象

