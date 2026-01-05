# 英文名称的 Flask 应用包装文件
# 用于 Vercel 部署，避免中文文件名导致的编码问题

import sys
import os
from pathlib import Path

# 设置 Vercel 环境变量
os.environ['VERCEL'] = '1'

# 添加当前目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 使用 importlib 动态加载主应用文件
import importlib.util

# 主应用文件路径
main_app_file = current_dir / "工作待办清单桌面应用_精美版.py"

if not main_app_file.exists():
    raise FileNotFoundError(f"Main application file not found: {main_app_file}")

# 动态加载主应用模块
app_file_path = str(main_app_file.resolve())
spec = importlib.util.spec_from_file_location("main_app", app_file_path)

if spec is None or spec.loader is None:
    raise ImportError(f"Failed to create module spec for: {app_file_path}")

main_module = importlib.util.module_from_spec(spec)
sys.modules['main_app'] = main_module

try:
    spec.loader.exec_module(main_module)
except Exception as e:
    raise ImportError(f"Failed to load main application module: {e}")

# 获取 Flask 应用实例
if not hasattr(main_module, 'app'):
    raise AttributeError("Flask app 'app' not found in main application module")

# 导出 Flask 应用
app = main_module.app

# 验证 app 是 Flask 实例
from flask import Flask
if not isinstance(app, Flask):
    raise TypeError(f"Expected Flask instance, got {type(app)}")

