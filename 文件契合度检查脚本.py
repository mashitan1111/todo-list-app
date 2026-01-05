#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件契合度检查脚本
用途：检查文件契合度问题（版本冲突、重复文件、引用不一致）
创建日期：2026-01-04
版本：V1.0
"""

import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 基础目录
BASE_DIR = Path(__file__).parent.parent

def check_version_conflicts():
    """检查版本冲突"""
    print("=" * 60)
    print("检查版本冲突...")
    print("=" * 60)
    
    conflicts = []
    
    # 检查Agent工作流程指南
    guide_dir = BASE_DIR / "RAG知识库/Agent工作流程指南"
    if guide_dir.exists():
        files = list(guide_dir.glob("*.md"))
        file_bases = defaultdict(list)
        
        for file in files:
            # 提取基础文件名（去除版本号）
            base_name = re.sub(r'_V\d+\.\d+', '', file.stem)
            file_bases[base_name].append(file)
        
        # 检查是否有多个版本
        for base_name, files in file_bases.items():
            if len(files) > 1:
                versions = [f.name for f in files]
                conflicts.append({
                    'base_name': base_name,
                    'files': versions,
                    'type': 'version_conflict'
                })
                print(f"⚠️  版本冲突: {base_name}")
                for f in files:
                    print(f"   - {f.name}")
    
    print(f"\n发现 {len(conflicts)} 个版本冲突")
    return conflicts

def check_duplicate_files():
    """检查重复文件"""
    print("\n" + "=" * 60)
    print("检查重复文件...")
    print("=" * 60)
    
    duplicates = []
    
    # 检查模板文件
    template_files = [
        ("工作记录系统/内容生成模板.md", 
         "RAG知识库/15_监管Skill库/05_工作效率Skill/02_内容生成模板.md"),
        ("工作记录系统/质量检查清单.md", 
         "RAG知识库/15_监管Skill库/05_工作效率Skill/03_质量检查清单.md"),
    ]
    
    for file1_path, file2_path in template_files:
        file1 = BASE_DIR / file1_path
        file2 = BASE_DIR / file2_path
        
        if file1.exists() and file2.exists():
            duplicates.append({
                'file1': file1_path,
                'file2': file2_path,
                'type': 'duplicate_template'
            })
            print(f"⚠️  重复文件:")
            print(f"   - {file1_path}")
            print(f"   - {file2_path}")
    
    print(f"\n发现 {len(duplicates)} 个重复文件")
    return duplicates

def check_reference_consistency():
    """检查引用一致性"""
    print("\n" + "=" * 60)
    print("检查引用一致性...")
    print("=" * 60)
    
    inconsistencies = []
    
    # 检查关键文件中的引用
    key_files = [
        "RAG知识库/Agent工作流程指南/00_Agent工作流程总指南_V3.0.md",
        "RAG知识库/Agent工作流程指南/01_每日工作流程SOP_V2.0.md",
    ]
    
    old_references = [
        "00_Agent工作流程总指南.md",
        "01_每日工作流程SOP.md",
    ]
    
    for key_file in key_files:
        file_path = BASE_DIR / key_file
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for old_ref in old_references:
                if old_ref in content:
                    inconsistencies.append({
                        'file': key_file,
                        'old_reference': old_ref,
                        'type': 'old_reference'
                    })
                    print(f"⚠️  旧引用: {key_file}")
                    print(f"   引用: {old_ref}")
    
    print(f"\n发现 {len(inconsistencies)} 个引用不一致")
    return inconsistencies

def generate_report(conflicts, duplicates, inconsistencies):
    """生成检查报告"""
    report_file = BASE_DIR / "工作记录系统" / f"文件契合度检查报告_{datetime.now().strftime('%Y%m%d')}.md"
    
    report = f"""# 文件契合度检查报告

## 【元数据】
- **检查日期**：{datetime.now().strftime('%Y-%m-%d %H:%M')}
- **版本**：V1.0

---

## 📊 检查结果

### 版本冲突
- **发现数量**：{len(conflicts)} 个

"""
    
    if conflicts:
        for conflict in conflicts:
            report += f"#### {conflict['base_name']}\n"
            report += f"- 文件：\n"
            for file in conflict['files']:
                report += f"  - `{file}`\n"
            report += "\n"
    else:
        report += "✅ 未发现版本冲突\n\n"
    
    report += f"""
### 重复文件
- **发现数量**：{len(duplicates)} 个

"""
    
    if duplicates:
        for dup in duplicates:
            report += f"- `{dup['file1']}` 与 `{dup['file2']}` 重复\n"
    else:
        report += "✅ 未发现重复文件\n\n"
    
    report += f"""
### 引用不一致
- **发现数量**：{len(inconsistencies)} 个

"""
    
    if inconsistencies:
        for inc in inconsistencies:
            report += f"- `{inc['file']}` 中引用了旧版本 `{inc['old_reference']}`\n"
    else:
        report += "✅ 未发现引用不一致\n\n"
    
    report += f"""
---

## 💡 建议

### P0级别（立即处理）
"""
    
    if conflicts or duplicates:
        report += "1. 归档旧版本文件\n"
        report += "2. 删除重复模板文件\n"
    
    if inconsistencies:
        report += "3. 更新所有旧引用为新版本\n"
    
    report += f"""
---

**报告生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    # 写入报告文件
    report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 已生成检查报告: {report_file}")
    return report_file

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("文件契合度检查脚本")
    print("=" * 60)
    print(f"工作目录: {BASE_DIR}")
    print()
    
    # 检查版本冲突
    conflicts = check_version_conflicts()
    
    # 检查重复文件
    duplicates = check_duplicate_files()
    
    # 检查引用一致性
    inconsistencies = check_reference_consistency()
    
    # 生成报告
    report_file = generate_report(conflicts, duplicates, inconsistencies)
    
    # 总结
    print("\n" + "=" * 60)
    print("检查完成总结")
    print("=" * 60)
    print(f"版本冲突: {len(conflicts)} 个")
    print(f"重复文件: {len(duplicates)} 个")
    print(f"引用不一致: {len(inconsistencies)} 个")
    print(f"检查报告: {report_file}")
    print("\n✅ 检查完成！")

if __name__ == "__main__":
    main()

