#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量检查模板
用途：通用批量检查脚本模板
创建日期：2026-01-04
版本：V1.0

使用方法：
1. 复制此模板文件
2. 修改 CONFIG 部分的配置
3. 根据需要修改检查函数
4. 运行脚本
"""

import re
from pathlib import Path
from datetime import datetime

# ==================== CONFIG 配置区域 ====================
# 请根据实际需求修改以下配置

# 基础目录（脚本所在目录的父目录）
BASE_DIR = Path(__file__).parent.parent.parent

# 需要检查的文件列表（相对路径）
FILES_TO_CHECK = [
    # 示例：添加需要检查的文件路径
    # "工作记录系统/文件1.md",
    # "RAG知识库/文件2.md",
]

# 检查规则（检查函数列表）
CHECK_RULES = [
    # 示例：检查元数据
    # lambda content: ('## 【元数据】' in content, '元数据检查'),
    # 示例：检查占位符
    # lambda content: ('待补充' not in content and 'TODO' not in content, '占位符检查'),
]

# 是否生成报告
GENERATE_REPORT = True

# 报告文件路径
REPORT_FILE = BASE_DIR / "工作记录系统" / f"批量检查报告_{datetime.now().strftime('%Y%m%d')}.md"

# ==================== 检查函数 ====================

def check_file(file_path):
    """检查单个文件"""
    if not file_path.exists():
        return {
            'file': str(file_path),
            'status': 'not_found',
            'checks': []
        }
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = []
        all_passed = True
        
        # 执行检查规则
        for check_func in CHECK_RULES:
            passed, check_name = check_func(content)
            checks.append({
                'name': check_name,
                'passed': passed
            })
            if not passed:
                all_passed = False
        
        return {
            'file': str(file_path),
            'status': 'passed' if all_passed else 'failed',
            'checks': checks
        }
        
    except Exception as e:
        return {
            'file': str(file_path),
            'status': 'error',
            'error': str(e),
            'checks': []
        }

def check_files():
    """批量检查文件"""
    print(f"🔍 开始批量检查文件...\n")
    
    results = []
    passed_count = 0
    failed_count = 0
    error_count = 0
    
    for file_path_str in FILES_TO_CHECK:
        file_path = BASE_DIR / file_path_str
        result = check_file(file_path)
        results.append(result)
        
        if result['status'] == 'passed':
            print(f"  ✅ 通过：{file_path_str}")
            passed_count += 1
        elif result['status'] == 'failed':
            print(f"  ❌ 失败：{file_path_str}")
            for check in result['checks']:
                if not check['passed']:
                    print(f"      - {check['name']}：未通过")
            failed_count += 1
        elif result['status'] == 'not_found':
            print(f"  ⚠️  未找到：{file_path_str}")
            error_count += 1
        else:
            print(f"  ❌ 错误：{file_path_str} - {result.get('error', '未知错误')}")
            error_count += 1
    
    print(f"\n📊 检查统计：")
    print(f"  ✅ 通过：{passed_count} 个文件")
    print(f"  ❌ 失败：{failed_count} 个文件")
    print(f"  ⚠️  错误：{error_count} 个文件")
    print(f"  📋 总计：{len(FILES_TO_CHECK)} 个文件")
    
    return results, passed_count, failed_count, error_count

def generate_report(results, passed_count, failed_count, error_count):
    """生成检查报告"""
    if not GENERATE_REPORT:
        return
    
    report = f"""# 批量检查报告

## 【元数据】
- **检查日期**：{datetime.now().strftime('%Y-%m-%d %H:%M')}
- **检查文件数**：{len(FILES_TO_CHECK)}
- **通过**：{passed_count} 个
- **失败**：{failed_count} 个
- **错误**：{error_count} 个
- **版本**：V1.0

---

## 📊 检查结果

"""
    
    # 按状态分组
    passed_files = [r for r in results if r['status'] == 'passed']
    failed_files = [r for r in results if r['status'] == 'failed']
    error_files = [r for r in results if r['status'] in ['not_found', 'error']]
    
    if passed_files:
        report += "### ✅ 通过的文件\n\n"
        for result in passed_files:
            report += f"- `{result['file']}`\n"
        report += "\n"
    
    if failed_files:
        report += "### ❌ 失败的文件\n\n"
        for result in failed_files:
            report += f"- `{result['file']}`\n"
            for check in result['checks']:
                if not check['passed']:
                    report += f"  - ❌ {check['name']}：未通过\n"
        report += "\n"
    
    if error_files:
        report += "### ⚠️  错误的文件\n\n"
        for result in error_files:
            report += f"- `{result['file']}`\n"
            if 'error' in result:
                report += f"  - 错误：{result['error']}\n"
        report += "\n"
    
    report += f"---\n\n**报告生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    
    # 写入报告文件
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📝 已生成检查报告：{REPORT_FILE}")

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 批量检查脚本")
    print("=" * 60)
    print()
    
    # 批量检查文件
    results, passed_count, failed_count, error_count = check_files()
    
    # 生成报告
    if GENERATE_REPORT:
        generate_report(results, passed_count, failed_count, error_count)
    
    print("\n" + "=" * 60)
    print("✅ 文件检查完成！")
    print("=" * 60)
    
    if passed_count > 0:
        print(f"\n✅ {passed_count} 个文件检查通过")
    if failed_count > 0:
        print(f"❌ {failed_count} 个文件检查失败")
    if error_count > 0:
        print(f"⚠️  {error_count} 个文件检查出错")

if __name__ == "__main__":
    main()

