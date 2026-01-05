#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新任务清单脚本
用途：自动更新任务清单文件，跟踪任务状态和进度
"""

import os
import re
from datetime import datetime
from pathlib import Path

# 工作目录
BASE_DIR = Path(__file__).parent.parent
TASK_FILE = BASE_DIR / "工作记录系统" / "任务清单.md"


def read_task_file():
    """读取任务清单文件"""
    if not TASK_FILE.exists():
        return None
    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def update_task_status(content, task_id, status, progress=None, completion_time=None):
    """更新任务状态"""
    # 查找任务
    pattern = rf'(### {re.escape(task_id)}:.*?\n)((?:- \*\*.*?\*\*：.*?\n)*)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"警告：找不到任务 {task_id}")
        return content
    
    task_header = match.group(1)
    task_details = match.group(2)
    
    # 更新状态
    task_details = re.sub(r'- \*\*状态\*\*：.*?\n', f'- **状态**：{status}\n', task_details)
    
    # 更新进度
    if progress is not None:
        if re.search(r'- \*\*完成度\*\*：', task_details):
            task_details = re.sub(r'- \*\*完成度\*\*：.*?\n', 
                                 f'- **完成度**：{progress}%\n', task_details)
        else:
            task_details += f'- **完成度**：{progress}%\n'
    
    # 更新完成时间
    if status == "已完成" and completion_time:
        if re.search(r'- \*\*完成时间\*\*：', task_details):
            task_details = re.sub(r'- \*\*完成时间\*\*：.*?\n', 
                                 f'- **完成时间**：{completion_time}\n', task_details)
        else:
            task_details += f'- **完成时间**：{completion_time}\n'
    
    # 更新开始时间（如果状态变为"进行中"）
    if status == "进行中":
        if not re.search(r'- \*\*开始时间\*\*：', task_details):
            start_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            task_details += f'- **开始时间**：{start_time}\n'
    
    new_task = task_header + task_details
    content = content.replace(match.group(0), new_task)
    
    return content


def add_new_task(content, task_id, description, priority, status="待处理"):
    """添加新任务"""
    # 根据优先级确定插入位置
    priority_sections = {
        "P0": "## 🚨 P0级别任务（立即处理）",
        "P1": "## ⚡ P1级别任务（高优先级）",
        "P2": "## 📝 P2级别任务（中优先级）",
        "P3": "## 📋 P3级别任务（低优先级）"
    }
    
    section_header = priority_sections.get(priority, "## 📝 P2级别任务（中优先级）")
    
    # 查找对应优先级部分
    pattern = rf'({re.escape(section_header)}\s*\n)'
    match = re.search(pattern, content)
    
    if not match:
        print(f"警告：找不到优先级部分 {priority}")
        return content
    
    # 创建新任务
    create_time = datetime.now().strftime("%Y-%m-%d")
    new_task = f"""
### {task_id}: {description}
- **优先级**：{priority}
- **状态**：{status}
- **创建时间**：{create_time}
- **完成度**：0%

"""
    
    # 插入到对应部分
    insert_pos = match.end()
    content = content[:insert_pos] + new_task + content[insert_pos:]
    
    return content


def update_task_statistics(content):
    """更新任务统计"""
    # 统计各优先级任务数
    p0_tasks = len(re.findall(r'### TASK-\d+:.*?\n.*?- \*\*优先级\*\*：P0', content, re.DOTALL))
    p1_tasks = len(re.findall(r'### TASK-\d+:.*?\n.*?- \*\*优先级\*\*：P1', content, re.DOTALL))
    p2_tasks = len(re.findall(r'### TASK-\d+:.*?\n.*?- \*\*优先级\*\*：P2', content, re.DOTALL))
    
    # 统计各状态任务数
    pending_tasks = len(re.findall(r'- \*\*状态\*\*：待处理', content))
    in_progress_tasks = len(re.findall(r'- \*\*状态\*\*：进行中', content))
    blocked_tasks = len(re.findall(r'- \*\*状态\*\*：已阻塞', content))
    completed_tasks = len(re.findall(r'- \*\*状态\*\*：已完成', content))
    
    # 更新统计部分
    stats_pattern = r'(### 按优先级统计\s*\n.*?\n)'
    stats_text = f"""### 按优先级统计
- **P0**：{p0_tasks}个
- **P1**：{p1_tasks}个
- **P2**：{p2_tasks}个

### 按状态统计
- **待处理**：{pending_tasks}个
- **进行中**：{in_progress_tasks}个
- **已阻塞**：{blocked_tasks}个
- **已完成**：{completed_tasks}个

"""
    
    content = re.sub(r'(## 📊 任务统计\s*\n)(.*?)(\n---)', 
                    r'\1' + stats_text + r'\3', content, flags=re.DOTALL)
    
    return content


def update_last_update_time(content):
    """更新最后更新时间"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    pattern = r'\*\*最后更新\*\*：.*?\n'
    content = re.sub(pattern, f'**最后更新**：{current_time}\n', content)
    return content


def update_task_list(task_id=None, description=None, priority=None, status=None, progress=None):
    """更新任务清单"""
    content = read_task_file()
    if content is None:
        print(f"错误：找不到任务清单文件 {TASK_FILE}")
        return False
    
    # 添加新任务
    if task_id and description and priority:
        content = add_new_task(content, task_id, description, priority, status or "待处理")
    
    # 更新任务状态
    if task_id and status:
        completion_time = datetime.now().strftime("%Y-%m-%d %H:%M") if status == "已完成" else None
        content = update_task_status(content, task_id, status, progress, completion_time)
    
    # 更新统计
    content = update_task_statistics(content)
    
    # 更新最后更新时间
    content = update_last_update_time(content)
    
    # 写回文件
    with open(TASK_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新任务清单：{TASK_FILE}")
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  添加任务: python 自动更新任务清单.py add <TASK-ID> <描述> <优先级>")
        print("  更新状态: python 自动更新任务清单.py update <TASK-ID> <状态> [进度]")
        print("示例:")
        print("  python 自动更新任务清单.py add TASK-010 '测试自动化脚本' P1")
        print("  python 自动更新任务清单.py update TASK-010 '已完成' 100")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "add":
        if len(sys.argv) < 5:
            print("错误：添加任务需要任务ID、描述和优先级")
            sys.exit(1)
        task_id = sys.argv[2]
        description = sys.argv[3]
        priority = sys.argv[4]
        update_task_list(task_id=task_id, description=description, priority=priority)
    
    elif action == "update":
        if len(sys.argv) < 4:
            print("错误：更新任务需要任务ID和状态")
            sys.exit(1)
        task_id = sys.argv[2]
        status = sys.argv[3]
        progress = int(sys.argv[4]) if len(sys.argv) > 4 else None
        update_task_list(task_id=task_id, status=status, progress=progress)
    
    else:
        print(f"错误：未知操作 {action}")
        sys.exit(1)

