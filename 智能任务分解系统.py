#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能任务分解系统
用途：自动任务分解和依赖管理
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque

# 工作目录
BASE_DIR = Path(__file__).parent.parent
TASK_FILE = BASE_DIR / "工作记录系统" / "任务清单.md"
DECOMPOSITION_FILE = BASE_DIR / "工作记录系统" / "任务分解记录.md"


def read_tasks():
    """读取任务清单"""
    if not TASK_FILE.exists():
        return None
    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def identify_task_type(task_description):
    """识别任务类型"""
    task_lower = task_description.lower()
    
    # 检查类任务
    if any(keyword in task_lower for keyword in ['检查', '审查', '验证', '审核']):
        return '检查'
    
    # 修复类任务
    if any(keyword in task_lower for keyword in ['修复', '更新', '删除', '归档']):
        return '修复'
    
    # 创建类任务
    if any(keyword in task_lower for keyword in ['创建', '建立', '生成', '制作']):
        return '创建'
    
    # 优化类任务
    if any(keyword in task_lower for keyword in ['优化', '改进', '提升', '增强']):
        return '优化'
    
    return '其他'


def decompose_task(task_description, task_type):
    """分解任务为子任务"""
    subtasks = []
    
    if task_type == '检查':
        subtasks = [
            '准备检查清单',
            '执行检查',
            '记录检查结果',
            '生成检查报告'
        ]
    
    elif task_type == '修复':
        subtasks = [
            '识别问题',
            '制定修复方案',
            '执行修复',
            '验证修复效果'
        ]
    
    elif task_type == '创建':
        subtasks = [
            '设计结构',
            '创建内容',
            '检查质量',
            '完成文档'
        ]
    
    elif task_type == '优化':
        subtasks = [
            '分析现状',
            '制定优化方案',
            '实施优化',
            '验证效果'
        ]
    
    else:
        subtasks = [
            '分析需求',
            '制定方案',
            '执行任务',
            '验证结果'
        ]
    
    return subtasks


def extract_task_dependencies(task_content):
    """提取任务依赖关系"""
    dependencies = {}
    
    if not task_content:
        return dependencies
    
    # 提取所有任务
    pattern = r'### (TASK-\d+):(.*?)\n((?:- \*\*.*?\*\*：.*?\n)*)'
    matches = re.findall(pattern, task_content, re.DOTALL)
    
    for task_id, desc, details in matches:
        # 提取依赖任务
        dep_match = re.search(r'- \*\*依赖任务\*\*：(.*?)\n', details)
        if dep_match:
            dep_str = dep_match.group(1).strip()
            if dep_str and dep_str != '无':
                deps = [d.strip() for d in dep_str.split('、') if d.strip()]
                dependencies[task_id] = {
                    'description': desc.strip(),
                    'dependencies': deps
                }
            else:
                dependencies[task_id] = {
                    'description': desc.strip(),
                    'dependencies': []
                }
        else:
            dependencies[task_id] = {
                'description': desc.strip(),
                'dependencies': []
            }
    
    return dependencies


def build_dependency_graph(dependencies):
    """构建依赖图"""
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    
    # 初始化所有任务
    for task_id in dependencies:
        in_degree[task_id] = 0
    
    # 构建图
    for task_id, info in dependencies.items():
        for dep in info['dependencies']:
            if dep in dependencies:
                graph[dep].append(task_id)
                in_degree[task_id] += 1
    
    return graph, in_degree


def find_critical_path(dependencies, graph, in_degree):
    """找到关键路径"""
    # 使用拓扑排序找到最长路径
    queue = deque()
    dist = {}
    
    # 初始化距离
    for task_id in dependencies:
        if in_degree[task_id] == 0:
            queue.append(task_id)
            dist[task_id] = 1
        else:
            dist[task_id] = 0
    
    # BFS计算最长路径
    while queue:
        current = queue.popleft()
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            dist[neighbor] = max(dist[neighbor], dist[current] + 1)
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # 找到最长路径
    max_dist = max(dist.values()) if dist else 0
    critical_tasks = [task_id for task_id, d in dist.items() if d == max_dist]
    
    return critical_tasks, max_dist


def identify_parallel_tasks(dependencies):
    """识别可并行执行的任务"""
    graph, in_degree = build_dependency_graph(dependencies)
    
    # 找到所有没有依赖的任务（可以并行执行）
    parallel_groups = []
    current_level = [task_id for task_id, degree in in_degree.items() if degree == 0]
    
    if current_level:
        parallel_groups.append(current_level)
    
    # 使用拓扑排序找到每一层的任务
    temp_in_degree = in_degree.copy()
    temp_graph = {k: v[:] for k, v in graph.items()}
    
    while current_level:
        next_level = []
        for task_id in current_level:
            for neighbor in temp_graph[task_id]:
                temp_in_degree[neighbor] -= 1
                if temp_in_degree[neighbor] == 0:
                    next_level.append(neighbor)
        
        if next_level:
            parallel_groups.append(next_level)
        current_level = next_level
    
    return parallel_groups


def optimize_execution_order(dependencies):
    """优化执行顺序"""
    graph, in_degree = build_dependency_graph(dependencies)
    
    # 拓扑排序
    queue = deque()
    for task_id, degree in in_degree.items():
        if degree == 0:
            queue.append(task_id)
    
    execution_order = []
    while queue:
        # 同一层的任务可以并行执行
        level_tasks = []
        level_size = len(queue)
        for _ in range(level_size):
            task_id = queue.popleft()
            level_tasks.append(task_id)
            execution_order.append(task_id)
            
            for neighbor in graph[task_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if level_tasks:
            execution_order.append(('parallel', level_tasks))
    
    return execution_order


def identify_blocked_tasks(dependencies, task_content):
    """识别阻塞任务"""
    blocked = []
    
    graph, in_degree = build_dependency_graph(dependencies)
    
    for task_id, info in dependencies.items():
        # 检查依赖任务是否完成
        for dep_task in info['dependencies']:
            dep_status = get_task_status(task_content, dep_task)
            if dep_status and dep_status != '已完成':
                blocked.append({
                    'task_id': task_id,
                    'description': info['description'],
                    'blocked_by': dep_task,
                    'reason': f'依赖任务 {dep_task} 未完成'
                })
    
    return blocked


def get_task_status(task_content, task_id):
    """获取任务状态"""
    if not task_content:
        return None
    
    pattern = rf'### {re.escape(task_id)}:.*?\n((?:- \*\*.*?\*\*：.*?\n)*)'
    match = re.search(pattern, task_content)
    if match:
        status_match = re.search(r'- \*\*状态\*\*：(.*?)\n', match.group(1))
        if status_match:
            return status_match.group(1).strip()
    return None


def decompose_and_analyze(task_description=None, task_id=None):
    """分解任务并分析"""
    print("🔍 开始任务分解和分析...")
    
    # 读取任务清单
    task_content = read_tasks()
    
    if not task_content:
        print("❌ 错误：找不到任务清单文件")
        return None
    
    # 如果提供了任务描述，分解新任务
    if task_description:
        task_type = identify_task_type(task_description)
        subtasks = decompose_task(task_description, task_type)
        
        print(f"\n📋 任务分解结果：{task_description}")
        print(f"   任务类型：{task_type}")
        print(f"   子任务数量：{len(subtasks)}")
        for i, subtask in enumerate(subtasks, 1):
            print(f"   {i}. {subtask}")
        
        return {
            'task_description': task_description,
            'task_type': task_type,
            'subtasks': subtasks
        }
    
    # 分析现有任务的依赖关系
    print("\n📊 分析任务依赖关系...")
    dependencies = extract_task_dependencies(task_content)
    print(f"   发现 {len(dependencies)} 个任务")
    
    # 构建依赖图
    print("\n📊 构建依赖图...")
    graph, in_degree = build_dependency_graph(dependencies)
    print(f"   依赖图构建完成")
    
    # 找到关键路径
    print("\n📊 查找关键路径...")
    critical_tasks, critical_length = find_critical_path(dependencies, graph, in_degree)
    print(f"   关键路径长度：{critical_length}")
    print(f"   关键任务：{', '.join(critical_tasks[:5])}")
    
    # 识别可并行执行的任务
    print("\n📊 识别可并行执行的任务...")
    parallel_groups = identify_parallel_tasks(dependencies)
    print(f"   发现 {len(parallel_groups)} 个并行组")
    for i, group in enumerate(parallel_groups[:3], 1):
        print(f"   并行组{i}：{len(group)}个任务可以并行执行")
    
    # 优化执行顺序
    print("\n📊 优化执行顺序...")
    execution_order = optimize_execution_order(dependencies)
    
    # 识别阻塞任务
    print("\n📊 识别阻塞任务...")
    blocked_tasks = identify_blocked_tasks(dependencies, task_content)
    print(f"   发现 {len(blocked_tasks)} 个阻塞任务")
    
    # 生成报告
    report = generate_decomposition_report(
        dependencies, critical_tasks, critical_length,
        parallel_groups, execution_order, blocked_tasks
    )
    
    # 保存报告
    save_decomposition_report(report)
    
    return {
        'dependencies': dependencies,
        'critical_tasks': critical_tasks,
        'critical_length': critical_length,
        'parallel_groups': parallel_groups,
        'execution_order': execution_order,
        'blocked_tasks': blocked_tasks,
        'report': report
    }


def generate_decomposition_report(dependencies, critical_tasks, critical_length,
                                  parallel_groups, execution_order, blocked_tasks):
    """生成分解报告"""
    report = "# 智能任务分解报告\n\n"
    report += f"## 【元数据】\n"
    report += f"- **分解时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += f"- **任务总数**：{len(dependencies)}个\n"
    report += f"- **版本**：V1.0\n\n"
    report += "---\n\n"
    
    # 依赖关系
    report += "## 📊 任务依赖关系\n\n"
    report += f"**总任务数**：{len(dependencies)}个\n"
    report += f"**有依赖关系的任务**：{len([d for d in dependencies.values() if d['dependencies']])}个\n\n"
    
    # 关键路径
    report += "## 🎯 关键路径\n\n"
    report += f"**关键路径长度**：{critical_length}个任务\n"
    report += f"**关键任务**：\n"
    for task_id in critical_tasks[:10]:
        desc = dependencies[task_id]['description']
        report += f"- `{task_id}`: {desc}\n"
    report += "\n"
    
    # 并行执行
    report += "## ⚡ 可并行执行的任务\n\n"
    report += f"**并行组数**：{len(parallel_groups)}个\n\n"
    for i, group in enumerate(parallel_groups[:5], 1):
        report += f"### 并行组{i}（{len(group)}个任务）\n"
        for task_id in group[:5]:
            desc = dependencies[task_id]['description']
            report += f"- `{task_id}`: {desc}\n"
        report += "\n"
    
    # 阻塞任务
    if blocked_tasks:
        report += "## ⚠️ 阻塞任务\n\n"
        report += f"**阻塞任务数**：{len(blocked_tasks)}个\n\n"
        for task in blocked_tasks[:5]:
            report += f"- `{task['task_id']}`: {task['description']}\n"
            report += f"  - 阻塞原因：{task['reason']}\n"
        report += "\n"
    
    # 优化后的执行顺序
    report += "## 🔄 优化后的执行顺序\n\n"
    report += "**建议执行顺序**：\n\n"
    level = 1
    for item in execution_order[:20]:
        if isinstance(item, tuple) and item[0] == 'parallel':
            report += f"**第{level}层（可并行执行）**：\n"
            for task_id in item[1][:5]:
                desc = dependencies[task_id]['description']
                report += f"- `{task_id}`: {desc}\n"
            report += "\n"
            level += 1
        elif isinstance(item, str):
            desc = dependencies[item]['description']
            report += f"{level}. `{item}`: {desc}\n"
            level += 1
    
    report += "\n---\n\n"
    report += "**最后更新**：" + datetime.now().strftime('%Y-%m-%d %H:%M') + "\n"
    
    return report


def save_decomposition_report(report):
    """保存分解报告"""
    with open(DECOMPOSITION_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 已保存任务分解报告：{DECOMPOSITION_FILE}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        task_description = sys.argv[1]
        decompose_and_analyze(task_description=task_description)
    else:
        decompose_and_analyze()

