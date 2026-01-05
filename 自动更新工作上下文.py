#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新工作上下文脚本
用途：自动更新工作上下文文件，记录任务完成情况和工作状态
"""

import os
import re
from datetime import datetime
from pathlib import Path

# 工作目录
BASE_DIR = Path(__file__).parent.parent
CONTEXT_FILE = BASE_DIR / "工作记录系统" / "工作上下文.md"


def read_context_file():
    """读取工作上下文文件"""
    if not CONTEXT_FILE.exists():
        return None
    with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def update_recent_tasks(content, task_description, date_str=None):
    """更新最近完成的任务"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 查找"最近完成的任务"部分
    pattern = r'(## ✅ 最近完成的任务\s*\n\s*### )(\d{4}-\d{2}-\d{2})'
    match = re.search(pattern, content)
    
    if match:
        # 如果找到今天的日期，在现有日期下添加任务
        if match.group(2) == date_str:
            # 在今天的任务列表中添加新任务
            task_pattern = rf'(### {date_str}\s*\n)((?:\d+\. ✅ .*\n)*)'
            task_match = re.search(task_pattern, content)
            if task_match:
                existing_tasks = task_match.group(2)
                # 计算下一个任务编号
                task_numbers = re.findall(r'(\d+)\.', existing_tasks)
                next_num = int(task_numbers[-1]) + 1 if task_numbers else 1
                new_task = f"{next_num}. ✅ {task_description}\n"
                content = content.replace(task_match.group(0), 
                                         task_match.group(1) + existing_tasks + new_task)
        else:
            # 添加新的日期部分
            new_section = f"\n### {date_str}\n1. ✅ {task_description}\n"
            content = re.sub(r'(## ✅ 最近完成的任务\s*\n)', 
                           r'\1' + new_section, content)
    else:
        # 如果没有找到，添加新部分
        new_section = f"\n## ✅ 最近完成的任务\n\n### {date_str}\n1. ✅ {task_description}\n"
        content = re.sub(r'(## 🔄 进行中的任务)', new_section + r'\n---\n\n\1', content)
    
    return content


def update_ongoing_tasks(content, task_description, status="已完成", progress=100):
    """更新进行中的任务状态"""
    # 查找任务描述
    pattern = rf'(⏳ \*\*{re.escape(task_description)}\*\*.*?\n)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # 更新状态
        old_text = match.group(1)
        new_text = old_text.replace("⏳", "✅" if status == "已完成" else "⏳")
        new_text = re.sub(r'- \*\*状态\*\*：.*?\n', f'- **状态**：{status}\n', new_text)
        new_text = re.sub(r'- \*\*进度\*\*：\d+%', f'- **进度**：{progress}%', new_text)
        if status == "已完成":
            completion_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_text = re.sub(r'- \*\*完成时间\*\*：.*?\n', 
                            f'- **完成时间**：{completion_time}\n', new_text, count=1)
            if "- **完成时间**：" not in new_text:
                new_text = re.sub(r'(- \*\*进度\*\*：\d+%\n)', 
                                 r'\1- **完成时间**：' + completion_time + '\n', new_text)
        content = content.replace(old_text, new_text)
    
    return content


def update_last_update_time(content):
    """更新最后更新时间"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    pattern = r'\*\*最后更新\*\*：.*?\n'
    content = re.sub(pattern, f'**最后更新**：{current_time}\n', content)
    return content


def update_context(task_description=None, task_status=None, task_progress=None):
    """更新工作上下文"""
    content = read_context_file()
    if content is None:
        print(f"错误：找不到工作上下文文件 {CONTEXT_FILE}")
        return False
    
    # 更新最近完成的任务
    if task_description and task_status == "已完成":
        content = update_recent_tasks(content, task_description)
    
    # 更新进行中的任务
    if task_description and task_status:
        content = update_ongoing_tasks(content, task_description, task_status, task_progress or 100)
    
    # 更新最后更新时间
    content = update_last_update_time(content)
    
    # 写回文件
    with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新工作上下文：{CONTEXT_FILE}")
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python 自动更新工作上下文.py <任务描述> [状态] [进度]")
        print("示例: python 自动更新工作上下文.py '创建优化工具文件' '已完成' 100")
        sys.exit(1)
    
    task_desc = sys.argv[1]
    task_status = sys.argv[2] if len(sys.argv) > 2 else "已完成"
    task_progress = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    
    update_context(task_desc, task_status, task_progress)

