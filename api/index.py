# Vercel无服务器函数入口
# 使用最标准的方式导出 Flask 应用

import os
import sys
from pathlib import Path

# 设置 Vercel 环境变量（必须在导入之前）
os.environ['VERCEL'] = '1'

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 直接导入 Flask 应用
from app import app

# Vercel 会自动识别 Flask 应用
# 直接导出即可，不需要额外的类型检查

