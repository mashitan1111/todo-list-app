# Vercel无服务器函数入口
# 这个文件用于Vercel部署，将Flask应用作为无服务器函数运行

import sys
import os
from pathlib import Path

# 设置Vercel环境变量（必须在导入应用之前设置）
os.environ['VERCEL'] = '1'

# 添加父目录到路径
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# 从英文名称的包装文件导入 Flask 应用
# 这样可以避免中文文件名在 Vercel 环境中的编码问题
try:
    from todo_app import app
except ImportError as e:
    # 如果导入失败，尝试直接动态加载
    import importlib.util
    from flask import Flask
    
    app_file = parent_dir / "工作待办清单桌面应用_精美版.py"
    if not app_file.exists():
        raise FileNotFoundError(f"Application file not found: {app_file}")
    
    app_file_path = str(app_file.resolve())
    spec = importlib.util.spec_from_file_location("main_app", app_file_path)
    
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to create module spec: {e}")
    
    main_module = importlib.util.module_from_spec(spec)
    sys.modules['main_app'] = main_module
    spec.loader.exec_module(main_module)
    
    if not hasattr(main_module, 'app'):
        raise AttributeError("Flask app not found in module")
    
    app = main_module.app
    
    if not isinstance(app, Flask):
        raise TypeError(f"Expected Flask instance, got {type(app)}")

# Vercel 会自动识别 Flask 应用
# 直接导出 app 对象即可

