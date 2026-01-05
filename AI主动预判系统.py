#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI主动预判系统
用途：AI主动预判用户需求，提前准备方案
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# 工作目录
BASE_DIR = Path(__file__).parent.parent
CONTEXT_FILE = BASE_DIR / "工作记录系统" / "工作上下文.md"
TASK_FILE = BASE_DIR / "工作记录系统" / "任务清单.md"
PREDICTION_FILE = BASE_DIR / "工作记录系统" / "AI预判记录.md"
PATTERN_FILE = BASE_DIR / "工作记录系统" / "预判模式库.md"  # 新增：预判模式库


def read_context():
    """读取工作上下文"""
    if not CONTEXT_FILE.exists():
        return None
    with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def read_tasks():
    """读取任务清单"""
    if not TASK_FILE.exists():
        return None
    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def analyze_recent_tasks(context_content):
    """分析最近完成的任务"""
    # 提取最近完成的任务
    pattern = r'## ✅ 最近完成的任务\s*\n\s*### (\d{4}-\d{2}-\d{2})\s*\n((?:\d+\. ✅ .*\n)*)'
    match = re.search(pattern, context_content)
    
    if not match:
        return []
    
    tasks = []
    task_lines = match.group(2).strip().split('\n')
    for line in task_lines:
        if '✅' in line:
            task_desc = re.sub(r'^\d+\.\s*✅\s*', '', line).strip()
            tasks.append({
                'description': task_desc,
                'date': match.group(1)
            })
    
    return tasks


def analyze_ongoing_tasks(context_content):
    """分析进行中的任务"""
    # 提取进行中的任务
    pattern = r'### (P0|P1|P2|P3)级别.*?\n((?:.*?⏳.*?\n)*)'
    matches = re.findall(pattern, context_content, re.DOTALL)
    
    tasks = []
    for priority, section in matches:
        # 提取任务描述
        task_pattern = r'⏳ \*\*(.*?)\*\*'
        task_matches = re.findall(task_pattern, section)
        for task_desc in task_matches:
            tasks.append({
                'description': task_desc,
                'priority': priority,
                'status': '进行中'
            })
    
    return tasks


def analyze_pending_tasks(context_content, task_content):
    """分析待处理的任务"""
    tasks = []
    
    # 从工作上下文提取待处理任务
    pattern = r'## 📋 待处理任务队列\s*\n(.*?)(?=\n---|\n##)'
    match = re.search(pattern, context_content, re.DOTALL)
    if match:
        task_lines = match.group(1).strip().split('\n')
        for line in task_lines:
            if '- [ ]' in line:
                task_desc = re.sub(r'^- \[ \]\s*', '', line).strip()
                tasks.append({
                    'description': task_desc,
                    'status': '待处理'
                })
    
    # 从任务清单提取待处理任务
    if task_content:
        pattern = r'- \*\*状态\*\*：待处理'
        pending_sections = re.findall(r'### (TASK-\d+:.*?)(?=\n### |\n##)', task_content, re.DOTALL)
        for section in pending_sections:
            task_id_match = re.search(r'TASK-\d+', section)
            desc_match = re.search(r'- \*\*描述\*\*：(.*?)\n', section)
            priority_match = re.search(r'- \*\*优先级\*\*：(P0|P1|P2|P3)', section)
            
            if task_id_match and desc_match:
                tasks.append({
                    'task_id': task_id_match.group(0),
                    'description': desc_match.group(1).strip(),
                    'priority': priority_match.group(1) if priority_match else 'P2',
                    'status': '待处理'
                })
    
    return tasks


def analyze_task_dependencies(task_content):
    """分析任务依赖关系"""
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
                dependencies[task_id] = {
                    'description': desc.strip(),
                    'dependencies': dep_str.split('、') if '、' in dep_str else [dep_str]
                }
    
    return dependencies


def identify_blocked_tasks(task_content, dependencies):
    """识别阻塞任务"""
    blocked = []
    
    if not task_content:
        return blocked
    
    # 检查每个任务的状态
    pattern = r'### (TASK-\d+):(.*?)\n((?:- \*\*.*?\*\*：.*?\n)*)'
    matches = re.findall(pattern, task_content, re.DOTALL)
    
    for task_id, desc, details in matches:
        status_match = re.search(r'- \*\*状态\*\*：(.*?)\n', details)
        if status_match and status_match.group(1) == '已阻塞':
            blocked.append({
                'task_id': task_id,
                'description': desc.strip(),
                'reason': '已阻塞'
            })
        
        # 检查依赖任务是否完成
        if task_id in dependencies:
            dep_tasks = dependencies[task_id]['dependencies']
            for dep_task in dep_tasks:
                dep_status = get_task_status(task_content, dep_task.strip())
                if dep_status and dep_status != '已完成':
                    blocked.append({
                        'task_id': task_id,
                        'description': desc.strip(),
                        'reason': f'依赖任务 {dep_task} 未完成'
                    })
    
    return blocked


def get_task_status(task_content, task_id):
    """获取任务状态"""
    pattern = rf'### {re.escape(task_id)}:.*?\n((?:- \*\*.*?\*\*：.*?\n)*)'
    match = re.search(pattern, task_content)
    if match:
        status_match = re.search(r'- \*\*状态\*\*：(.*?)\n', match.group(1))
        if status_match:
            return status_match.group(1).strip()
    return None


def predict_next_tasks(context_content, task_content):
    """预测下一步任务"""
    predictions = []
    
    # 1. 分析阻塞任务
    dependencies = analyze_task_dependencies(task_content)
    blocked_tasks = identify_blocked_tasks(task_content, dependencies)
    
    if blocked_tasks:
        predictions.append({
            'type': 'blocked',
            'priority': 'P0',
            'message': f'发现 {len(blocked_tasks)} 个阻塞任务，建议优先处理',
            'tasks': blocked_tasks[:3]  # 只显示前3个
        })
    
    # 2. 分析P0级别待处理任务
    pending_tasks = analyze_pending_tasks(context_content, task_content)
    p0_tasks = [t for t in pending_tasks if t.get('priority') == 'P0']
    
    if p0_tasks:
        predictions.append({
            'type': 'p0_pending',
            'priority': 'P0',
            'message': f'发现 {len(p0_tasks)} 个P0级别待处理任务',
            'tasks': p0_tasks[:3]
        })
    
    # 3. 分析P1级别待处理任务
    p1_tasks = [t for t in pending_tasks if t.get('priority') == 'P1']
    
    if p1_tasks:
        predictions.append({
            'type': 'p1_pending',
            'priority': 'P1',
            'message': f'发现 {len(p1_tasks)} 个P1级别待处理任务',
            'tasks': p1_tasks[:3]
        })
    
    # 4. 分析进行中的任务
    ongoing_tasks = analyze_ongoing_tasks(context_content)
    
    if ongoing_tasks:
        predictions.append({
            'type': 'ongoing',
            'priority': 'P1',
            'message': f'发现 {len(ongoing_tasks)} 个进行中的任务',
            'tasks': ongoing_tasks[:3]
        })
    
    return predictions


def generate_prediction_report(predictions):
    """生成预判报告"""
    report = "# AI主动预判报告\n\n"
    report += f"## 【元数据】\n"
    report += f"- **预判时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += f"- **预判数量**：{len(predictions)}个\n"
    report += f"- **版本**：V1.0\n\n"
    report += "---\n\n"
    
    if not predictions:
        report += "## ✅ 当前状态良好\n\n"
        report += "未发现需要立即处理的任务。\n"
        return report
    
    report += "## 🎯 预判结果\n\n"
    
    for i, pred in enumerate(predictions, 1):
        priority_icon = {
            'P0': '🚨',
            'P1': '⚡',
            'P2': '📝',
            'P3': '📋'
        }.get(pred['priority'], '📋')
        
        report += f"### {i}. {priority_icon} {pred['message']}\n\n"
        
        if 'tasks' in pred and pred['tasks']:
            report += "**相关任务**：\n"
            for task in pred['tasks']:
                task_id = task.get('task_id', '')
                desc = task.get('description', '')
                if task_id:
                    report += f"- `{task_id}`: {desc}\n"
                else:
                    report += f"- {desc}\n"
            report += "\n"
        
        # 根据类型提供建议
        if pred['type'] == 'blocked':
            report += "**建议**：优先处理阻塞任务，解除阻塞后可以继续执行后续任务。\n\n"
        elif pred['type'] == 'p0_pending':
            report += "**建议**：立即处理P0级别任务，这些是阻塞性问题。\n\n"
        elif pred['type'] == 'p1_pending':
            report += "**建议**：尽快处理P1级别任务，这些是重要问题。\n\n"
        elif pred['type'] == 'ongoing':
            report += "**建议**：继续推进进行中的任务，确保按时完成。\n\n"
    
    report += "---\n\n"
    report += "**最后更新**：" + datetime.now().strftime('%Y-%m-%d %H:%M') + "\n"
    
    return report


def save_prediction(predictions):
    """保存预判结果"""
    report = generate_prediction_report(predictions)
    
    with open(PREDICTION_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 已保存预判报告：{PREDICTION_FILE}")
    return report


def generate_suggestions(predictions):
    """生成建议方案"""
    suggestions = []
    
    for pred in predictions:
        if pred['type'] == 'blocked':
            suggestions.append({
                'action': '处理阻塞任务',
                'tasks': [t.get('task_id') or t.get('description') for t in pred.get('tasks', [])],
                'priority': 'P0'
            })
        elif pred['type'] == 'p0_pending':
            suggestions.append({
                'action': '处理P0级别任务',
                'tasks': [t.get('task_id') or t.get('description') for t in pred.get('tasks', [])],
                'priority': 'P0'
            })
        elif pred['type'] == 'p1_pending':
            suggestions.append({
                'action': '处理P1级别任务',
                'tasks': [t.get('task_id') or t.get('description') for t in pred.get('tasks', [])],
                'priority': 'P1'
            })
    
    return suggestions


def load_prediction_patterns():
    """加载预判模式库（新增 - V4.0效率优化）"""
    if not PATTERN_FILE.exists():
        return {}
    
    patterns = {}
    with open(PATTERN_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取历史模式
    pattern_sections = re.findall(r'### 模式\d+\.\d+：(.*?)\n(.*?)(?=\n### |\n##)', content, re.DOTALL)
    for pattern_name, pattern_content in pattern_sections:
        # 提取准确率
        accuracy_match = re.search(r'\*\*准确率\*\*：(\d+)%', pattern_content)
        accuracy = int(accuracy_match.group(1)) if accuracy_match else 0
        
        # 提取预判规则
        rules_match = re.search(r'\*\*预判规则\*\*：\n((?:- .*\n)*)', pattern_content)
        rules = []
        if rules_match:
            rule_lines = rules_match.group(1).strip().split('\n')
            for line in rule_lines:
                if line.startswith('- '):
                    rules.append(line[2:].strip())
        
        patterns[pattern_name.strip()] = {
            'accuracy': accuracy,
            'rules': rules,
            'content': pattern_content
        }
    
    return patterns

def predict_user_needs():
    """预判用户需求（增强版 - 集成预判模式库）"""
    print("🔍 开始分析工作上下文和任务清单...")
    
    # 加载预判模式库
    print("📚 加载预判模式库...")
    patterns = load_prediction_patterns()
    print(f"   加载 {len(patterns)} 个预判模式")
    
    # 读取文件
    context_content = read_context()
    task_content = read_tasks()
    
    if not context_content:
        print("❌ 错误：找不到工作上下文文件")
        return None
    
    # 分析
    print("📊 分析最近完成的任务...")
    recent_tasks = analyze_recent_tasks(context_content)
    print(f"   发现 {len(recent_tasks)} 个最近完成的任务")
    
    print("📊 分析进行中的任务...")
    ongoing_tasks = analyze_ongoing_tasks(context_content)
    print(f"   发现 {len(ongoing_tasks)} 个进行中的任务")
    
    print("📊 分析待处理的任务...")
    pending_tasks = analyze_pending_tasks(context_content, task_content)
    print(f"   发现 {len(pending_tasks)} 个待处理的任务")
    
    print("📊 分析任务依赖关系...")
    dependencies = analyze_task_dependencies(task_content)
    print(f"   发现 {len(dependencies)} 个任务有依赖关系")
    
    print("📊 识别阻塞任务...")
    blocked_tasks = identify_blocked_tasks(task_content, dependencies)
    print(f"   发现 {len(blocked_tasks)} 个阻塞任务")
    
    # 预测（增强：结合预判模式库）
    print("🎯 预测下一步任务（结合预判模式库）...")
    predictions = predict_next_tasks(context_content, task_content)
    
    # 应用预判模式库规则（增强预判准确性）
    if patterns:
        print("📊 应用预判模式库规则...")
        enhanced_predictions = []
        for pred in predictions:
            # 根据模式库调整预判优先级和准确性
            for pattern_name, pattern_data in patterns.items():
                if pattern_data['accuracy'] >= 80:  # 只使用高准确率模式
                    # 检查预判是否匹配模式
                    if any(rule in str(pred) for rule in pattern_data['rules']):
                        pred['pattern_matched'] = pattern_name
                        pred['confidence'] = pattern_data['accuracy'] / 100
                        break
            enhanced_predictions.append(pred)
        predictions = enhanced_predictions
    
    print(f"   生成 {len(predictions)} 个预判结果")
    
    # 生成建议
    suggestions = generate_suggestions(predictions)
    
    # 保存预判结果
    report = save_prediction(predictions)
    
    # 输出预判结果
    print("\n" + "="*60)
    print("AI主动预判结果")
    print("="*60)
    print(report)
    
    return {
        'predictions': predictions,
        'suggestions': suggestions,
        'report': report
    }


if __name__ == "__main__":
    predict_user_needs()

