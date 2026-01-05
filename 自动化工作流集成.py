#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化工作流集成脚本
用途：集成所有自动化脚本到工作流程中
"""

import sys
import subprocess
from pathlib import Path

# 脚本目录
SCRIPT_DIR = Path(__file__).parent


def run_script(script_name, *args):
    """运行Python脚本"""
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        print(f"错误：找不到脚本 {script_name}")
        return False
    
    cmd = [sys.executable, str(script_path)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"错误：{result.stderr}")
        return False


def update_context_after_task(task_description, status="已完成", progress=100):
    """任务完成后更新工作上下文"""
    print(f"\n📝 更新工作上下文...")
    return run_script("自动更新工作上下文.py", task_description, status, str(progress))


def update_task_after_completion(task_id, status="已完成", progress=100):
    """任务完成后更新任务清单"""
    print(f"\n📋 更新任务清单...")
    return run_script("自动更新任务清单.py", "update", task_id, status, str(progress))


def update_cache_after_check(file_path, check_type, check_result, priority="P2"):
    """检查完成后更新缓存"""
    print(f"\n💾 更新检查缓存...")
    return run_script("智能缓存管理器.py", "update", file_path, check_type, check_result, priority)


def complete_task_workflow(task_id, task_description, file_path=None, check_type=None, check_result=None, priority="P2"):
    """完成任务工作流"""
    print(f"\n🔄 执行任务完成工作流：{task_id}")
    print(f"   任务描述：{task_description}")
    
    success = True
    
    # 1. 更新工作上下文
    if not update_context_after_task(task_description):
        success = False
    
    # 2. 更新任务清单
    if not update_task_after_completion(task_id):
        success = False
    
    # 3. 更新检查缓存（如果有）
    if file_path and check_type and check_result:
        if not update_cache_after_check(file_path, check_type, check_result, priority):
            success = False
    
    if success:
        print(f"\n✅ 任务完成工作流执行成功：{task_id}")
    else:
        print(f"\n❌ 任务完成工作流执行失败：{task_id}")
    
    return success


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法:")
        print("  完成任务: python 自动化工作流集成.py complete <TASK-ID> <任务描述> [文件路径] [检查类型] [结果] [优先级]")
        print("示例:")
        print("  python 自动化工作流集成.py complete TASK-010 '创建优化工具文件'")
        print("  python 自动化工作流集成.py complete TASK-011 '检查RAG知识库' 'RAG知识库/README.md' '全面检查' '通过' P1")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "complete":
        if len(sys.argv) < 4:
            print("错误：需要任务ID和任务描述")
            sys.exit(1)
        
        task_id = sys.argv[2]
        task_description = sys.argv[3]
        file_path = sys.argv[4] if len(sys.argv) > 4 else None
        check_type = sys.argv[5] if len(sys.argv) > 5 else None
        check_result = sys.argv[6] if len(sys.argv) > 6 else None
        priority = sys.argv[7] if len(sys.argv) > 7 else "P2"
        
        complete_task_workflow(task_id, task_description, file_path, check_type, check_result, priority)
    
    else:
        print(f"错误：未知操作 {action}")
        sys.exit(1)

