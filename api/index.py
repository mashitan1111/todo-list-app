# Vercel无服务器函数入口
# 确保 Flask 应用被正确识别

import os
import sys
from pathlib import Path

# 设置 Vercel 环境变量（必须在导入之前）
os.environ['VERCEL'] = '1'

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入 Flask 应用
from app import app as flask_app
from flask import Flask

# 验证 app 是 Flask 实例
if not isinstance(flask_app, Flask):
    raise TypeError(f"Expected Flask instance, got {type(flask_app)}")

# 导出为 app（Vercel 期望的名称）
# 确保类型信息正确
app = flask_app

# 显式设置 WSGI 应用（某些情况下需要）
__all__ = ['app']

