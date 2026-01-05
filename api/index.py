# Vercel无服务器函数入口
# 这个文件用于Vercel部署，将Flask应用作为无服务器函数运行

import sys
import os
from pathlib import Path

# 设置Vercel环境变量
os.environ['VERCEL'] = '1'

# 添加父目录到路径，以便导入应用
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# 导入Flask应用
# 使用 importlib 直接加载模块，避免中文文件名编码问题
import importlib.util
from flask import Flask

app_file = parent_dir / "工作待办清单桌面应用_精美版.py"
if not app_file.exists():
    raise FileNotFoundError(f"Application file not found: {app_file}")

# 使用绝对路径，确保编码正确
app_file_str = str(app_file.absolute())

spec = importlib.util.spec_from_file_location("todo_app", app_file_str)
if spec is None or spec.loader is None:
    raise ImportError(f"Failed to create spec for: {app_file_str}")

module = importlib.util.module_from_spec(spec)
sys.modules['todo_app'] = module

# 执行模块加载
try:
    spec.loader.exec_module(module)
except Exception as e:
    raise ImportError(f"Failed to load module: {e}")

# 获取 Flask app 实例
if not hasattr(module, 'app'):
    raise AttributeError("Flask app not found in module")

app_instance = module.app

# 验证 app 是 Flask 实例
if not isinstance(app_instance, Flask):
    raise TypeError(f"Expected Flask instance, got {type(app_instance)}")

# 直接导出 app，Vercel 会自动识别 Flask 应用
app = app_instance

