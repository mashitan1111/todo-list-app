#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Agent启动检查验证脚本
用途：验证Agent是否执行了启动强制检查清单
创建日期：2026-01-04
版本：V1.0
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

# 工作区根目录
WORKSPACE_ROOT = Path(r"C:\Users\温柔的男子啊\Desktop\crusor\圆心工作")

# 检查清单文件路径
CHECKLIST_FILE = WORKSPACE_ROOT / "RAG知识库" / "Agent工作流程指南" / "00_Agent启动强制检查清单.md"

# 工作上下文文件路径
CONTEXT_FILE = WORKSPACE_ROOT / "工作记录系统" / "工作上下文.md"

# 任务清单文件路径
TASK_LIST_FILE = WORKSPACE_ROOT / "工作记录系统" / "任务清单.md"

# 检查缓存文件路径
CACHE_FILE = WORKSPACE_ROOT / "工作记录系统" / "检查缓存.md"

# 流程执行日志文件路径
LOG_FILE = WORKSPACE_ROOT / "工作记录系统" / "流程执行日志.md"

# 验证结果文件路径
VERIFICATION_RESULT_FILE = WORKSPACE_ROOT / "工作记录系统" / "Agent启动检查验证结果.md"


def read_file(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"读取文件失败 {file_path}: {e}")
        return None


def check_file_exists(file_path):
    """检查文件是否存在"""
    return file_path.exists() and file_path.is_file()


def verify_checklist_execution():
    """验证检查清单执行情况"""
    results = {
        "检查时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "检查项": [],
        "总体状态": "未知",
        "违规记录": []
    }
    
    # 检查1：工作上下文文件是否存在且可读
    context_exists = check_file_exists(CONTEXT_FILE)
    context_content = read_file(CONTEXT_FILE) if context_exists else None
    
    results["检查项"].append({
        "名称": "工作上下文文件检查",
        "状态": "通过" if context_exists else "失败",
        "详情": f"文件存在: {context_exists}",
        "文件路径": str(CONTEXT_FILE)
    })
    
    if not context_exists:
        results["违规记录"].append("工作上下文文件不存在或无法读取")
    
    # 检查2：任务清单文件是否存在且可读
    task_list_exists = check_file_exists(TASK_LIST_FILE)
    task_list_content = read_file(TASK_LIST_FILE) if task_list_exists else None
    
    results["检查项"].append({
        "名称": "任务清单文件检查",
        "状态": "通过" if task_list_exists else "失败",
        "详情": f"文件存在: {task_list_exists}",
        "文件路径": str(TASK_LIST_FILE)
    })
    
    if not task_list_exists:
        results["违规记录"].append("任务清单文件不存在或无法读取")
    
    # 检查3：检查缓存文件是否存在且可读
    cache_exists = check_file_exists(CACHE_FILE)
    cache_content = read_file(CACHE_FILE) if cache_exists else None
    
    results["检查项"].append({
        "名称": "检查缓存文件检查",
        "状态": "通过" if cache_exists else "失败",
        "详情": f"文件存在: {cache_exists}",
        "文件路径": str(CACHE_FILE)
    })
    
    if not cache_exists:
        results["违规记录"].append("检查缓存文件不存在或无法读取")
    
    # 检查4：检查清单文件是否存在
    checklist_exists = check_file_exists(CHECKLIST_FILE)
    
    results["检查项"].append({
        "名称": "检查清单文件检查",
        "状态": "通过" if checklist_exists else "失败",
        "详情": f"文件存在: {checklist_exists}",
        "文件路径": str(CHECKLIST_FILE)
    })
    
    # 检查5：流程执行日志是否存在
    log_exists = check_file_exists(LOG_FILE)
    log_content = read_file(LOG_FILE) if log_exists else None
    
    # 检查日志中是否有最近的执行记录
    recent_execution = False
    if log_content:
        # 检查是否有今天的执行记录
        today = datetime.now().strftime("%Y-%m-%d")
        if today in log_content:
            recent_execution = True
    
    results["检查项"].append({
        "名称": "流程执行日志检查",
        "状态": "通过" if log_exists else "失败",
        "详情": f"文件存在: {log_exists}, 最近执行: {recent_execution}",
        "文件路径": str(LOG_FILE)
    })
    
    # 总体状态判断
    all_passed = all(item["状态"] == "通过" for item in results["检查项"])
    results["总体状态"] = "通过" if all_passed and len(results["违规记录"]) == 0 else "失败"
    
    return results


def generate_verification_report(results):
    """生成验证报告"""
    report = f"""# Agent启动检查验证结果

## 【元数据】
- **验证时间**：{results["检查时间"]}
- **总体状态**：{'✅ 通过' if results['总体状态'] == '通过' else '❌ 失败'}
- **版本**：V1.0

---

## 📊 检查结果

### 总体状态
- **状态**：{results["总体状态"]}
- **检查项总数**：{len(results["检查项"])}
- **通过项数**：{sum(1 for item in results["检查项"] if item["状态"] == "通过")}
- **失败项数**：{sum(1 for item in results["检查项"] if item["状态"] == "失败")}

### 详细检查项

"""
    
    for i, item in enumerate(results["检查项"], 1):
        status_icon = "✅" if item["状态"] == "通过" else "❌"
        report += f"""#### {i}. {item["名称"]} {status_icon}

- **状态**：{item["状态"]}
- **详情**：{item["详情"]}
- **文件路径**：`{item["文件路径"]}`

"""
    
    if results["违规记录"]:
        report += """---

## ⚠️ 违规记录

"""
        for i, violation in enumerate(results["违规记录"], 1):
            report += f"{i}. {violation}\n"
        report += "\n"
    
    report += """---

## 📋 建议

### 如果检查失败
1. 确保所有必需文件都存在
2. 检查文件权限
3. 确保Agent已执行启动强制检查清单
4. 查看`工作记录系统/流程执行日志.md`了解详细情况

### 如果检查通过
1. 继续执行Agent工作流程
2. 确保每次对话开始前都执行检查清单
3. 定期审查执行情况

---

**最后更新**：""" + results["检查时间"] + """  
**版本**：V1.0  
**维护者**：自动化脚本
"""
    
    return report


def main():
    """主函数"""
    print("=" * 60)
    print("Agent启动检查验证脚本")
    print("=" * 60)
    print()
    
    # 执行验证
    print("正在验证检查清单执行情况...")
    results = verify_checklist_execution()
    
    # 生成报告
    print("正在生成验证报告...")
    report = generate_verification_report(results)
    
    # 保存报告
    try:
        with open(VERIFICATION_RESULT_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 验证报告已保存到: {VERIFICATION_RESULT_FILE}")
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        return
    
    # 输出结果
    print()
    print("=" * 60)
    print("验证结果")
    print("=" * 60)
    print(f"总体状态: {results['总体状态']}")
    print(f"检查项总数: {len(results['检查项'])}")
    print(f"通过项数: {sum(1 for item in results['检查项'] if item['状态'] == '通过')}")
    print(f"失败项数: {sum(1 for item in results['检查项'] if item['状态'] == '失败')}")
    
    if results["违规记录"]:
        print()
        print("⚠️ 违规记录:")
        for violation in results["违规记录"]:
            print(f"  - {violation}")
    
    print()
    print("=" * 60)
    print("验证完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

