#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理占位符脚本
用途：移除工作待办清单中的所有空占位符
"""

import re
from pathlib import Path

# 工作目录
BASE_DIR = Path(__file__).parent.parent
TODO_FILE = BASE_DIR / "工作待办清单.md"

# 占位符模式
PLACEHOLDER_PATTERNS = [
    r'- \[ \] \[任务\d+\]',
    r'- \[ \] \[紧急事项\d+\]',
    r'- \[ \] \[高优先级事项\d+\]',
    r'- \[ \] \[任务1\]',
    r'- \[ \] \[任务2\]',
    r'- \[ \] \[紧急事项1\]',
    r'- \[ \] \[紧急事项2\]',
    r'- \[ \] \[高优先级事项1\]',
    r'- \[ \] \[高优先级事项2\]',
]


def clean_placeholders():
    """清理占位符"""
    print("🔍 开始清理占位符...")
    print(f"📁 文件：{TODO_FILE.relative_to(BASE_DIR)}")
    print()
    
    if not TODO_FILE.exists():
        print(f"❌ 错误：找不到文件 {TODO_FILE}")
        return
    
    # 读取文件
    with open(TODO_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    removed_count = 0
    
    # 移除所有占位符
    for pattern in PLACEHOLDER_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            removed_count += len(matches)
            content = re.sub(pattern + r'\s*\n?', '', content)
    
    # 清理多余的空行（连续3个或以上空行变为2个）
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 如果内容有变化，保存文件
    if content != original_content:
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 已清理 {removed_count} 个占位符")
        print(f"✅ 文件已更新")
    else:
        print("ℹ️  未找到需要清理的占位符")
    
    print()


if __name__ == "__main__":
    print("="*60)
    print("清理工作待办清单占位符")
    print("="*60)
    print()
    
    clean_placeholders()
    
    print("="*60)
    print("✅ 清理完成")
    print("="*60)

