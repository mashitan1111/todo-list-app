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
try:
    from 工作待办清单桌面应用_精美版 import app
except ImportError as e:
    # 如果导入失败，尝试直接导入
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "app", 
        parent_dir / "工作待办清单桌面应用_精美版.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = module.app

# Vercel需要导出handler
handler = app

