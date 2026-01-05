#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作上下文自动更新机制
用途：每次对话后自动更新工作上下文
创建日期：2026-01-04
版本：V1.0
"""

import re
from pathlib import Path
from datetime import datetime

# 基础目录
BASE_DIR = Path(__file__).parent.parent
CONTEXT_FILE = BASE_DIR / "工作记录系统" / "工作上下文.md"

def update_context_date():
    """更新工作上下文的日期"""
    if not CONTEXT_FILE.exists():
        return False
    
    with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新更新日期
    today = datetime.now().strftime('%Y-%m-%d')
    content = re.sub(r'- \*\*更新日期\*\*：\d{4}-\d{2}-\d{2}', 
                    f'- **更新日期**：{today}', content)
    content = re.sub(r'\*\*2026-\d{2}-\d{2}\*\*', 
                    f'**{today}**', content)
    
    # 更新最后更新时间
    content = re.sub(r'\*\*最后更新\*\*：\d{4}-\d{2}-\d{2}', 
                    f'**最后更新**：{today}', content)
    
    with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新工作上下文日期到 {today}")
    return True

def add_completed_task(task_description):
    """添加已完成的任务"""
    if not CONTEXT_FILE.exists():
        return False
    
    with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 查找今天的任务部分
    today_pattern = rf'### {today}'
    if today_pattern not in content:
        # 如果没有今天的部分，添加
        recent_tasks_pattern = r'(## ✅ 最近完成的任务\s*\n)'
        match = re.search(recent_tasks_pattern, content)
        if match:
            insert_pos = match.end()
            new_section = f"\n### {today}\n1. ✅ {task_description}\n"
            content = content[:insert_pos] + new_section + content[insert_pos:]
    else:
        # 如果已有今天的部分，追加任务
        today_section_pattern = rf'(### {today}\s*\n)((?:\d+\. ✅ .*\n)*)'
        match = re.search(today_section_pattern, content)
        if match:
            existing_tasks = match.group(2)
            task_num = len(existing_tasks.strip().split('\n')) if existing_tasks.strip() else 0
            new_task = f"{task_num + 1}. ✅ {task_description}\n"
            content = content.replace(match.group(0), match.group(1) + existing_tasks + new_task)
    
    with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已添加已完成任务：{task_description}")
    return True

def update_ongoing_task(task_description, status="进行中"):
    """更新进行中的任务"""
    if not CONTEXT_FILE.exists():
        return False
    
    with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找任务并更新状态
    task_pattern = rf'⏳ \*\*{re.escape(task_description)}\*\*'
    if task_pattern in content:
        if status == "已完成":
            content = re.sub(task_pattern, f'✅ **{task_description}**', content)
        else:
            content = re.sub(task_pattern, f'⏳ **{task_description}**', content)
    
    with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新任务状态：{task_description} - {status}")
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("工作上下文自动更新机制")
    print("=" * 60)
    
    # 更新日期
    update_context_date()
    
    print("\n✅ 工作上下文已更新！")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "add-task" and len(sys.argv) > 2:
            task_desc = sys.argv[2]
            add_completed_task(task_desc)
        elif action == "update-task" and len(sys.argv) > 3:
            task_desc = sys.argv[2]
            status = sys.argv[3]
            update_ongoing_task(task_desc, status)
        else:
            print("用法:")
            print("  更新日期: python 工作上下文自动更新机制.py")
            print("  添加任务: python 工作上下文自动更新机制.py add-task '任务描述'")
            print("  更新任务: python 工作上下文自动更新机制.py update-task '任务描述' '状态'")
    else:
        main()

