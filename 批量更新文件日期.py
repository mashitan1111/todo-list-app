#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新文件日期脚本
用途：批量更新所有2024-12-19的文件日期到2026-01-03
"""

import re
from pathlib import Path

# 工作目录
BASE_DIR = Path(__file__).parent.parent

# 要更新的日期
OLD_DATE = "2024-12-19"
NEW_DATE = "2026-01-04"

# 统计
updated_files = []
skipped_files = []
error_files = []


def update_file_dates(file_path, content):
    """更新单个文件的日期"""
    try:
        original_content = content
        
        # 匹配多种日期格式，使用捕获组保留原始格式
        # 格式1: - **更新日期**：2024-12-19
        # 格式2: - 更新日期：2024-12-19
        # 格式3: **更新日期**：2024-12-19
        # 格式4: 更新日期：2024-12-19
        # 格式5: 最后更新：2024-12-19
        # 等等...
        
        patterns = [
            # 匹配 - **更新日期**：2024-12-19 格式
            (r'(- \*\*更新日期\*\*：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 - 更新日期：2024-12-19 格式
            (r'(- 更新日期：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 **更新日期**：2024-12-19 格式
            (r'(\*\*更新日期\*\*：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 更新日期：2024-12-19 格式
            (r'(更新日期：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 最后更新：2024-12-19 格式
            (r'(最后更新：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 评分日期：2024-12-19 格式
            (r'(评分日期：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 审查日期：2024-12-19 格式
            (r'(审查日期：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 创建日期：2024-12-19 格式
            (r'(创建日期：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 预判时间：2024-12-19 格式
            (r'(预判时间：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 分解时间：2024-12-19 格式
            (r'(分解时间：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 - **最后更新**：2024-12-19 格式
            (r'(- \*\*最后更新\*\*：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
            # 匹配 - 最后更新：2024-12-19 格式
            (r'(- 最后更新：)\s*' + re.escape(OLD_DATE), r'\1' + NEW_DATE),
        ]
        
        updated = False
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                updated = True
        
        # 如果内容有变化，保存文件
        if updated and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, None
        else:
            return False, "未找到需要更新的日期"
    
    except Exception as e:
        return False, str(e)


def scan_and_update():
    """扫描并更新所有文件"""
    print(f"🔍 开始扫描文件，查找日期为 {OLD_DATE} 的文件...")
    print(f"📁 工作目录：{BASE_DIR}")
    print()
    
    # 扫描所有Markdown文件
    md_files = list(BASE_DIR.rglob("*.md"))
    
    print(f"📊 找到 {len(md_files)} 个Markdown文件")
    print()
    
    for file_path in md_files:
        # 跳过工具脚本目录
        if '工具脚本' in str(file_path):
            continue
        
        # 检查文件是否包含旧日期
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if OLD_DATE in content:
                print(f"📝 处理：{file_path.relative_to(BASE_DIR)}")
                success, error = update_file_dates(file_path, content)
                
                if success:
                    updated_files.append(str(file_path.relative_to(BASE_DIR)))
                    print(f"   ✅ 已更新")
                elif error:
                    if "未找到需要更新的日期" not in error:
                        error_files.append((str(file_path.relative_to(BASE_DIR)), error))
                        print(f"   ❌ 错误：{error}")
                    else:
                        skipped_files.append(str(file_path.relative_to(BASE_DIR)))
                        print(f"   ⏭️  跳过：{error}")
        except Exception as e:
            error_files.append((str(file_path.relative_to(BASE_DIR)), str(e)))
            print(f"   ❌ 读取错误：{e}")
    
    print()
    print("="*60)
    print("更新完成统计")
    print("="*60)
    print(f"✅ 已更新文件：{len(updated_files)} 个")
    print(f"⏭️  跳过文件：{len(skipped_files)} 个")
    print(f"❌ 错误文件：{len(error_files)} 个")
    print()
    
    if updated_files:
        print("已更新的文件：")
        for file in updated_files[:20]:  # 只显示前20个
            print(f"  - {file}")
        if len(updated_files) > 20:
            print(f"  ... 还有 {len(updated_files) - 20} 个文件")
        print()
    
    if error_files:
        print("错误文件：")
        for file, error in error_files:
            print(f"  - {file}: {error}")
        print()


if __name__ == "__main__":
    print("="*60)
    print("批量更新文件日期")
    print("="*60)
    print(f"旧日期：{OLD_DATE}")
    print(f"新日期：{NEW_DATE}")
    print()
    
    scan_and_update()
    
    print("="*60)
    print("✅ 批量更新完成")
    print("="*60)

