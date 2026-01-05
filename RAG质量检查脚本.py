#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG知识库质量检查脚本
功能：自动检查RAG知识库内容质量，生成质量报告和修复清单
"""

import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 工作目录
BASE_DIR = Path(__file__).parent.parent
RAG_DIR = BASE_DIR / "RAG知识库"
OUTPUT_DIR = BASE_DIR / "工作记录系统"

# 禁止的占位符
FORBIDDEN_PLACEHOLDERS = [
    r'待补充',
    r'待更新',
    r'待审核',
    r'待确认',
    r'\[待补充\]',
    r'\[待更新\]',
    r'\[待审核\]',
    r'\[待确认\]',
    r'TBD',
    r'TODO',
    r'待明确',
    r'待完善',
]

# 元数据必填字段
METADATA_FIELDS = ['用途', '更新日期', '版本']


def find_md_files(directory):
    """查找所有Markdown文件"""
    md_files = []
    for root, dirs, files in os.walk(directory):
        # 跳过归档目录
        if '归档文件' in root or '归档' in root:
            continue
        for file in files:
            if file.endswith('.md'):
                md_files.append(Path(root) / file)
    return md_files


def check_placeholders(file_path):
    """检查占位符"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                for pattern in FORBIDDEN_PLACEHOLDERS:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            'line': i,
                            'content': line.strip(),
                            'pattern': pattern
                        })
    except Exception as e:
        issues.append({
            'line': 0,
            'content': f'读取文件失败: {e}',
            'pattern': 'FILE_ERROR'
        })
    
    return issues


def check_metadata(file_path):
    """检查元数据完整性"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查是否有元数据部分
            if '## 【元数据】' not in content and '## 元数据' not in content:
                issues.append({
                    'type': 'missing_metadata',
                    'message': '缺少元数据部分'
                })
                return issues
            
            # 检查必填字段
            for field in METADATA_FIELDS:
                pattern = rf'\*\*{field}\*\*'
                if not re.search(pattern, content):
                    issues.append({
                        'type': 'missing_field',
                        'field': field,
                        'message': f'缺少元数据字段: {field}'
                    })
            
            # 检查更新日期是否过时（超过30天）
            date_pattern = r'\*\*更新日期\*\*[：:]\s*(\d{4}-\d{2}-\d{2})'
            match = re.search(date_pattern, content)
            if match:
                update_date_str = match.group(1)
                try:
                    update_date = datetime.strptime(update_date_str, '%Y-%m-%d')
                    days_old = (datetime.now() - update_date).days
                    if days_old > 30:
                        issues.append({
                            'type': 'outdated_date',
                            'date': update_date_str,
                            'days_old': days_old,
                            'message': f'更新日期过时: {update_date_str} (已过{days_old}天)'
                        })
                except ValueError:
                    issues.append({
                        'type': 'invalid_date',
                        'date': update_date_str,
                        'message': f'更新日期格式错误: {update_date_str}'
                    })
    except Exception as e:
        issues.append({
            'type': 'read_error',
            'message': f'读取文件失败: {e}'
        })
    
    return issues


def check_file_references(file_path, all_files):
    """检查文件引用"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 查找文件引用（@符号或文件路径）
            # 匹配 @文件名.md 或 `路径/文件名.md`
            ref_patterns = [
                r'@([^\s]+\.md)',
                r'`([^\s`]+\.md)`',
                r'\[([^\]]+\.md)\]',
            ]
            
            referenced_files = set()
            for pattern in ref_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    referenced_files.add(match)
            
            # 检查引用的文件是否存在
            file_dir = file_path.parent
            for ref_file in referenced_files:
                # 尝试多种路径解析方式
                ref_paths = [
                    file_dir / ref_file,
                    RAG_DIR / ref_file,
                    RAG_DIR / ref_file.split('/')[-1],  # 只取文件名
                ]
                
                found = False
                for ref_path in ref_paths:
                    if ref_path.exists() and ref_path in all_files:
                        found = True
                        break
                
                if not found:
                    issues.append({
                        'type': 'missing_reference',
                        'file': ref_file,
                        'message': f'引用的文件不存在: {ref_file}'
                    })
    except Exception as e:
        issues.append({
            'type': 'read_error',
            'message': f'读取文件失败: {e}'
        })
    
    return issues


def check_business_logic(file_path):
    """检查业务逻辑"""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 检查时间轴逻辑错误（如"21:00-21:00"）
            time_pattern = r'(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})'
            matches = re.findall(time_pattern, content)
            for match in matches:
                start_hour, start_min = int(match[0]), int(match[1])
                end_hour, end_min = int(match[2]), int(match[3])
                
                start_time = start_hour * 60 + start_min
                end_time = end_hour * 60 + end_min
                
                if start_time >= end_time:
                    time_str = f"{match[0]}:{match[1]}-{match[2]}:{match[3]}"
                    issues.append({
                        'type': 'time_logic_error',
                        'time': time_str,
                        'message': f'时间轴逻辑错误: {time_str} (结束时间应晚于开始时间)'
                    })
            
            # 检查价格一致性（简化检查）
            price_patterns = [
                r'12\.9[元块]',
                r'12980[元块]',
                r'16980[元块]',
            ]
            # 这里可以添加更复杂的价格一致性检查
            
    except Exception as e:
        issues.append({
            'type': 'read_error',
            'message': f'读取文件失败: {e}'
        })
    
    return issues


def check_version_conflicts(file_path, all_files):
    """检查版本冲突"""
    issues = []
    file_name = file_path.name
    
    # 检查是否有多个版本的文件
    if '_V' in file_name or '_v' in file_name:
        # 提取基础文件名（去掉版本号）
        base_name = re.sub(r'_[Vv]\d+\.\d+.*', '', file_name)
        base_name = re.sub(r'_\d+\.\d+.*', '', base_name)
        
        # 查找同一目录下的其他版本
        same_dir = file_path.parent
        for other_file in same_dir.glob('*.md'):
            if other_file != file_path:
                other_name = other_file.name
                if base_name in other_name or other_name.startswith(base_name.split('_')[0]):
                    issues.append({
                        'type': 'version_conflict',
                        'conflict_file': other_file.name,
                        'message': f'可能存在版本冲突: {file_name} 和 {other_file.name}'
                    })
    
    return issues


def generate_quality_report(issues_by_file, all_files):
    """生成质量报告"""
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%Y-%m-%d %H:%M')
    
    # 统计问题
    total_files = len(all_files)
    files_with_issues = len(issues_by_file)
    total_issues = sum(len(issues) for issues in issues_by_file.values())
    
    # 按优先级分类问题
    p0_issues = []  # 占位符、业务逻辑错误
    p1_issues = []  # 元数据、文件引用
    p2_issues = []  # 版本冲突、日期过时
    
    for file_path, issues in issues_by_file.items():
        rel_path = file_path.relative_to(BASE_DIR)
        for issue in issues:
            issue_entry = {
                'file': str(rel_path),
                'issue': issue
            }
            
            if issue.get('pattern') or issue.get('type') == 'time_logic_error':
                p0_issues.append(issue_entry)
            elif issue.get('type') in ['missing_metadata', 'missing_field', 'missing_reference']:
                p1_issues.append(issue_entry)
            else:
                p2_issues.append(issue_entry)
    
    report = f"""# RAG知识库质量检查报告

## 【元数据】
- **检查日期**：{time_str}
- **检查范围**：RAG知识库所有文件
- **总文件数**：{total_files}个
- **有问题文件数**：{files_with_issues}个
- **总问题数**：{total_issues}个
- **版本**：V1.0

---

## 📊 检查统计

### 总体情况
- **总文件数**：{total_files}个
- **有问题文件数**：{files_with_issues}个
- **问题文件占比**：{files_with_issues/total_files*100:.1f}%
- **总问题数**：{total_issues}个
- **平均每文件问题数**：{total_issues/total_files:.2f}个

### 问题分布
- **P0级别（严重）**：{len(p0_issues)}个
- **P1级别（重要）**：{len(p1_issues)}个
- **P2级别（中等）**：{len(p2_issues)}个

---

## 🚨 P0级别问题（立即修复）

### 占位符问题
"""
    
    # 添加P0级别问题
    placeholder_issues = [i for i in p0_issues if i['issue'].get('pattern')]
    if placeholder_issues:
        report += f"\n**发现 {len(placeholder_issues)} 个占位符问题：**\n\n"
        for entry in placeholder_issues[:20]:  # 只显示前20个
            issue = entry['issue']
            report += f"- **文件**：`{entry['file']}`\n"
            if issue.get('line'):
                report += f"  - **行号**：{issue['line']}\n"
            report += f"  - **问题**：{issue.get('content', issue.get('pattern', ''))}\n"
            report += f"  - **类型**：占位符\n\n"
    else:
        report += "\n✅ 未发现占位符问题\n\n"
    
    # 业务逻辑错误
    logic_issues = [i for i in p0_issues if i['issue'].get('type') == 'time_logic_error']
    if logic_issues:
        report += f"\n### 业务逻辑错误\n\n"
        report += f"**发现 {len(logic_issues)} 个业务逻辑错误：**\n\n"
        for entry in logic_issues[:10]:
            issue = entry['issue']
            report += f"- **文件**：`{entry['file']}`\n"
            report += f"  - **问题**：{issue.get('message', '')}\n\n"
    else:
        report += "\n### 业务逻辑错误\n\n✅ 未发现业务逻辑错误\n\n"
    
    # 添加P1级别问题
    report += f"""---

## ⚠️ P1级别问题（本周修复）

### 元数据问题
"""
    
    metadata_issues = [i for i in p1_issues if 'metadata' in i['issue'].get('type', '') or 'field' in i['issue'].get('type', '')]
    if metadata_issues:
        report += f"\n**发现 {len(metadata_issues)} 个元数据问题：**\n\n"
        for entry in metadata_issues[:15]:
            issue = entry['issue']
            report += f"- **文件**：`{entry['file']}`\n"
            report += f"  - **问题**：{issue.get('message', '')}\n\n"
    else:
        report += "\n✅ 未发现元数据问题\n\n"
    
    # 文件引用问题
    ref_issues = [i for i in p1_issues if i['issue'].get('type') == 'missing_reference']
    if ref_issues:
        report += f"\n### 文件引用问题\n\n"
        report += f"**发现 {len(ref_issues)} 个文件引用问题：**\n\n"
        for entry in ref_issues[:15]:
            issue = entry['issue']
            report += f"- **文件**：`{entry['file']}`\n"
            report += f"  - **问题**：{issue.get('message', '')}\n\n"
    else:
        report += "\n### 文件引用问题\n\n✅ 未发现文件引用问题\n\n"
    
    # 添加P2级别问题
    report += f"""---

## 📋 P2级别问题（本月修复）

### 版本冲突
"""
    
    version_issues = [i for i in p2_issues if i['issue'].get('type') == 'version_conflict']
    if version_issues:
        report += f"\n**发现 {len(version_issues)} 个版本冲突：**\n\n"
        for entry in version_issues[:10]:
            issue = entry['issue']
            report += f"- **文件**：`{entry['file']}`\n"
            report += f"  - **问题**：{issue.get('message', '')}\n\n"
    else:
        report += "\n✅ 未发现版本冲突\n\n"
    
    # 日期过时问题
    date_issues = [i for i in p2_issues if i['issue'].get('type') == 'outdated_date']
    if date_issues:
        report += f"\n### 更新日期过时\n\n"
        report += f"**发现 {len(date_issues)} 个日期过时问题：**\n\n"
        for entry in date_issues[:10]:
            issue = entry['issue']
            report += f"- **文件**：`{entry['file']}`\n"
            report += f"  - **问题**：{issue.get('message', '')}\n\n"
    else:
        report += "\n### 更新日期过时\n\n✅ 未发现日期过时问题\n\n"
    
    # 添加修复清单
    report += f"""---

## 📋 修复清单

### 立即修复（P0级别）
"""
    
    if p0_issues:
        report += f"\n**共 {len(p0_issues)} 个问题需要立即修复：**\n\n"
        for i, entry in enumerate(p0_issues[:10], 1):
            report += f"{i}. **文件**：`{entry['file']}`\n"
            report += f"   - **问题**：{entry['issue'].get('message', entry['issue'].get('content', ''))}\n"
            report += f"   - **修复建议**：根据问题类型进行修复\n\n"
    else:
        report += "\n✅ 无P0级别问题\n\n"
    
    report += f"""
### 本周修复（P1级别）
"""
    
    if p1_issues:
        report += f"\n**共 {len(p1_issues)} 个问题需要本周修复：**\n\n"
        for i, entry in enumerate(p1_issues[:10], 1):
            report += f"{i}. **文件**：`{entry['file']}`\n"
            report += f"   - **问题**：{entry['issue'].get('message', '')}\n\n"
    else:
        report += "\n✅ 无P1级别问题\n\n"
    
    report += f"""
### 本月修复（P2级别）
"""
    
    if p2_issues:
        report += f"\n**共 {len(p2_issues)} 个问题需要本月修复：**\n\n"
        for i, entry in enumerate(p2_issues[:10], 1):
            report += f"{i}. **文件**：`{entry['file']}`\n"
            report += f"   - **问题**：{entry['issue'].get('message', '')}\n\n"
    else:
        report += "\n✅ 无P2级别问题\n\n"
    
    # 添加修复进度跟踪
    report += f"""---

## 📈 修复进度跟踪

### 修复状态
- **待修复**：{total_issues}个
- **已修复**：0个
- **修复率**：0%

### 修复优先级
1. **P0级别**：{len(p0_issues)}个（立即修复）
2. **P1级别**：{len(p1_issues)}个（本周修复）
3. **P2级别**：{len(p2_issues)}个（本月修复）

---

## 📚 相关文档

### 质量检查标准
- `RAG知识库/00_质量检查机制.md` - 质量检查机制
- `RAG知识库/15_监管Skill库/01_监管标准Skill/01_评分标准.md` - 评分标准

### 修复指南
- `RAG知识库/00_质量检查机制.md` - 修复标准
- `RAG知识库优化方案.md` - 优化方案

---

**报告生成时间**：{time_str}  
**下次检查时间**：下次运行脚本时
"""
    
    return report


def main():
    """主函数"""
    print("=" * 60)
    print("RAG知识库质量检查脚本")
    print("=" * 60)
    print()
    
    # 查找所有Markdown文件
    print("📖 正在扫描RAG知识库文件...")
    all_files = find_md_files(RAG_DIR)
    print(f"   找到 {len(all_files)} 个Markdown文件")
    
    # 检查所有文件
    issues_by_file = defaultdict(list)
    
    print("\n🔍 正在检查文件质量...")
    for i, file_path in enumerate(all_files, 1):
        if i % 10 == 0:
            print(f"   已检查 {i}/{len(all_files)} 个文件...")
        
        # 检查占位符
        placeholder_issues = check_placeholders(file_path)
        for issue in placeholder_issues:
            issues_by_file[file_path].append(issue)
        
        # 检查元数据
        metadata_issues = check_metadata(file_path)
        for issue in metadata_issues:
            issues_by_file[file_path].append(issue)
        
        # 检查文件引用
        ref_issues = check_file_references(file_path, all_files)
        for issue in ref_issues:
            issues_by_file[file_path].append(issue)
        
        # 检查业务逻辑
        logic_issues = check_business_logic(file_path)
        for issue in logic_issues:
            issues_by_file[file_path].append(issue)
        
        # 检查版本冲突
        version_issues = check_version_conflicts(file_path, all_files)
        for issue in version_issues:
            issues_by_file[file_path].append(issue)
    
    # 只保留有问题的文件
    issues_by_file = {k: v for k, v in issues_by_file.items() if v}
    
    print(f"\n✅ 检查完成！发现 {len(issues_by_file)} 个文件有问题")
    
    # 生成质量报告
    print("\n📝 正在生成质量报告...")
    report = generate_quality_report(issues_by_file, all_files)
    
    # 保存报告
    now = datetime.now()
    date_str = now.strftime('%Y%m%d')
    report_file = OUTPUT_DIR / f"RAG知识库质量检查报告_{date_str}.md"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✅ 质量报告已保存：{report_file}")
    except Exception as e:
        print(f"❌ 保存报告失败：{e}")
        return
    
    # 生成修复清单
    print("\n📋 正在生成修复清单...")
    fix_list = generate_fix_list(issues_by_file)
    fix_list_file = OUTPUT_DIR / f"RAG知识库修复清单_{date_str}.md"
    
    try:
        with open(fix_list_file, 'w', encoding='utf-8') as f:
            f.write(fix_list)
        print(f"✅ 修复清单已保存：{fix_list_file}")
    except Exception as e:
        print(f"❌ 保存修复清单失败：{e}")
    
    print("\n" + "=" * 60)
    print("✅ RAG知识库质量检查完成！")
    print("=" * 60)
    print(f"\n📄 质量报告：{report_file}")
    print(f"📋 修复清单：{fix_list_file}")
    print(f"\n💡 提示：请根据报告优先级修复问题")


def generate_fix_list(issues_by_file):
    """生成修复清单"""
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    
    # 按优先级分类
    p0_files = []
    p1_files = []
    p2_files = []
    
    for file_path, issues in issues_by_file.items():
        rel_path = file_path.relative_to(BASE_DIR)
        has_p0 = any(issue.get('pattern') or issue.get('type') == 'time_logic_error' for issue in issues)
        has_p1 = any(issue.get('type') in ['missing_metadata', 'missing_field', 'missing_reference'] for issue in issues)
        
        file_entry = {
            'path': str(rel_path),
            'issues': issues
        }
        
        if has_p0:
            p0_files.append(file_entry)
        elif has_p1:
            p1_files.append(file_entry)
        else:
            p2_files.append(file_entry)
    
    fix_list = f"""# RAG知识库修复清单

## 【元数据】
- **生成日期**：{date_str}
- **版本**：V1.0
- **用途**：跟踪RAG知识库质量问题修复进度

---

## 🚨 P0级别修复清单（立即修复）

### 占位符清理
"""
    
    placeholder_files = [f for f in p0_files if any(issue.get('pattern') for issue in f['issues'])]
    if placeholder_files:
        fix_list += f"\n**共 {len(placeholder_files)} 个文件需要清理占位符：**\n\n"
        for i, file_entry in enumerate(placeholder_files, 1):
            fix_list += f"{i}. **文件**：`{file_entry['path']}`\n"
            placeholder_issues = [issue for issue in file_entry['issues'] if issue.get('pattern')]
            fix_list += f"   - **占位符数量**：{len(placeholder_issues)}个\n"
            fix_list += f"   - **修复状态**：待修复\n"
            fix_list += f"   - **修复建议**：逐一替换占位符为实际内容\n\n"
    else:
        fix_list += "\n✅ 无占位符问题\n\n"
    
    fix_list += f"""
### 业务逻辑错误修复
"""
    
    logic_files = [f for f in p0_files if any(issue.get('type') == 'time_logic_error' for issue in f['issues'])]
    if logic_files:
        fix_list += f"\n**共 {len(logic_files)} 个文件需要修复业务逻辑错误：**\n\n"
        for i, file_entry in enumerate(logic_files, 1):
            fix_list += f"{i}. **文件**：`{file_entry['path']}`\n"
            logic_issues = [issue for issue in file_entry['issues'] if issue.get('type') == 'time_logic_error']
            fix_list += f"   - **错误数量**：{len(logic_issues)}个\n"
            fix_list += f"   - **修复状态**：待修复\n\n"
    else:
        fix_list += "\n✅ 无业务逻辑错误\n\n"
    
    fix_list += f"""
---

## ⚠️ P1级别修复清单（本周修复）

### 元数据补充
"""
    
    metadata_files = [f for f in p1_files if any('metadata' in issue.get('type', '') or 'field' in issue.get('type', '') for issue in f['issues'])]
    if metadata_files:
        fix_list += f"\n**共 {len(metadata_files)} 个文件需要补充元数据：**\n\n"
        for i, file_entry in enumerate(metadata_files[:20], 1):
            fix_list += f"{i}. **文件**：`{file_entry['path']}`\n"
            fix_list += f"   - **修复状态**：待修复\n\n"
    else:
        fix_list += "\n✅ 无元数据问题\n\n"
    
    fix_list += f"""
### 文件引用修复
"""
    
    ref_files = [f for f in p1_files if any(issue.get('type') == 'missing_reference' for issue in f['issues'])]
    if ref_files:
        fix_list += f"\n**共 {len(ref_files)} 个文件需要修复文件引用：**\n\n"
        for i, file_entry in enumerate(ref_files[:20], 1):
            fix_list += f"{i}. **文件**：`{file_entry['path']}`\n"
            fix_list += f"   - **修复状态**：待修复\n\n"
    else:
        fix_list += "\n✅ 无文件引用问题\n\n"
    
    fix_list += f"""
---

## 📋 P2级别修复清单（本月修复）

### 版本冲突处理
"""
    
    version_files = [f for f in p2_files if any(issue.get('type') == 'version_conflict' for issue in f['issues'])]
    if version_files:
        fix_list += f"\n**共 {len(version_files)} 个文件需要处理版本冲突：**\n\n"
        for i, file_entry in enumerate(version_files[:10], 1):
            fix_list += f"{i}. **文件**：`{file_entry['path']}`\n"
            fix_list += f"   - **修复状态**：待修复\n\n"
    else:
        fix_list += "\n✅ 无版本冲突\n\n"
    
    fix_list += f"""
---

## 📊 修复进度

### 总体进度
- **总问题数**：{sum(len(f['issues']) for f in p0_files + p1_files + p2_files)}个
- **已修复**：0个
- **待修复**：{sum(len(f['issues']) for f in p0_files + p1_files + p2_files)}个
- **修复率**：0%

### 按优先级
- **P0级别**：{sum(len(f['issues']) for f in p0_files)}个（待修复）
- **P1级别**：{sum(len(f['issues']) for f in p1_files)}个（待修复）
- **P2级别**：{sum(len(f['issues']) for f in p2_files)}个（待修复）

---

**最后更新**：{date_str}
"""
    
    return fix_list


if __name__ == "__main__":
    main()

