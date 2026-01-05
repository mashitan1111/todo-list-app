#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量内容更新模板
用途：通用批量内容更新脚本模板
创建日期：2026-01-04
版本：V1.0

使用方法：
1. 复制此模板文件
2. 修改 CONFIG 部分的配置
3. 根据需要修改更新函数
4. 运行脚本
"""

import re
from pathlib import Path
from datetime import datetime

# ==================== CONFIG 配置区域 ====================
# 请根据实际需求修改以下配置

# 基础目录（脚本所在目录的父目录）
BASE_DIR = Path(__file__).parent.parent.parent

# 需要更新的文件列表（相对路径）
FILES_TO_UPDATE = [
    # 示例：添加需要更新的文件路径
    # "工作记录系统/文件1.md",
    # "RAG知识库/文件2.md",
]

# 更新规则（正则表达式模式 → 替换内容）
UPDATE_RULES = [
    # 示例：更新日期
    # (r'更新日期.*?：\d{4}-\d{2}-\d{2}', f'更新日期：{datetime.now().strftime("%Y-%m-%d")}'),
    # 示例：更新版本号
    # (r'版本.*?：V\d+\.\d+', '版本：V2.0'),
]

# 是否备份原文件
BACKUP_FILES = True

# ==================== 更新函数 ====================

def backup_file(file_path):
    """备份文件"""
    if BACKUP_FILES:
        backup_path = file_path.with_suffix(file_path.suffix + '.bak')
        if file_path.exists():
            shutil.copy2(file_path, backup_path)
            return backup_path
    return None

def update_file_content(file_path):
    """更新文件内容"""
    if not file_path.exists():
        return False, "文件不存在"
    
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 应用更新规则
        for pattern, replacement in UPDATE_RULES:
            if isinstance(replacement, str):
                content = re.sub(pattern, replacement, content)
            elif callable(replacement):
                # 如果replacement是函数，使用函数处理
                content = replacement(content)
        
        # 如果内容有变化，写入文件
        if content != original_content:
            # 备份原文件
            backup_file(file_path)
            
            # 写入更新后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, "已更新"
        else:
            return True, "无需更新"
            
    except Exception as e:
        return False, str(e)

def update_files():
    """批量更新文件"""
    print(f"📝 开始批量更新文件...\n")
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for file_path_str in FILES_TO_UPDATE:
        file_path = BASE_DIR / file_path_str
        
        if not file_path.exists():
            print(f"  ⚠️  未找到：{file_path_str}")
            skipped_count += 1
            continue
        
        try:
            success, message = update_file_content(file_path)
            if success:
                if message == "已更新":
                    print(f"  ✅ 已更新：{file_path_str}")
                    updated_count += 1
                else:
                    print(f"  ⏭️  跳过：{file_path_str}（{message}）")
                    skipped_count += 1
            else:
                print(f"  ❌ 更新失败：{file_path_str} - {message}")
                error_count += 1
                
        except Exception as e:
            print(f"  ❌ 更新失败：{file_path_str} - {str(e)}")
            error_count += 1
    
    print(f"\n📊 更新统计：")
    print(f"  ✅ 成功更新：{updated_count} 个文件")
    print(f"  ⏭️  跳过：{skipped_count} 个文件")
    print(f"  ❌ 更新失败：{error_count} 个文件")
    print(f"  📋 总计：{len(FILES_TO_UPDATE)} 个文件")
    
    return updated_count, skipped_count, error_count

def main():
    """主函数"""
    print("=" * 60)
    print("📝 批量内容更新脚本")
    print("=" * 60)
    print()
    
    # 批量更新文件
    updated_count, skipped_count, error_count = update_files()
    
    print("\n" + "=" * 60)
    print("✅ 文件更新完成！")
    print("=" * 60)
    
    if updated_count > 0:
        print(f"\n✅ 成功更新 {updated_count} 个文件")
    if skipped_count > 0:
        print(f"⏭️  跳过 {skipped_count} 个文件（无需更新）")
    if error_count > 0:
        print(f"❌ 有 {error_count} 个文件更新失败")

if __name__ == "__main__":
    import shutil
    main()

