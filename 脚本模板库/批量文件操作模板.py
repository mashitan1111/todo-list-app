#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量文件操作模板
用途：通用批量文件操作脚本模板
创建日期：2026-01-04
版本：V1.0

使用方法：
1. 复制此模板文件
2. 修改 CONFIG 部分的配置
3. 根据需要修改操作函数
4. 运行脚本
"""

import os
import shutil
from pathlib import Path

# ==================== CONFIG 配置区域 ====================
# 请根据实际需求修改以下配置

# 基础目录（脚本所在目录的父目录）
BASE_DIR = Path(__file__).parent.parent.parent

# 目标目录（操作后的文件存放位置）
TARGET_DIR = BASE_DIR / "目标文件夹"  # 修改为实际目标文件夹

# 需要操作的文件列表（相对路径）
FILES_TO_OPERATE = [
    # 示例：添加需要操作的文件路径
    # "工作记录系统/文件1.md",
    # "工作记录系统/文件2.md",
]

# 操作类型：'move'（移动）、'copy'（复制）、'delete'（删除）
OPERATION_TYPE = 'move'  # 修改为实际操作类型

# 是否保持目录结构
KEEP_DIR_STRUCTURE = True

# ==================== 操作函数 ====================

def create_directories():
    """创建必要的目录结构"""
    print("📁 创建目录结构...")
    
    if OPERATION_TYPE == 'delete':
        return  # 删除操作不需要创建目录
    
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    if KEEP_DIR_STRUCTURE:
        # 创建子目录结构
        for file_path in FILES_TO_OPERATE:
            target = TARGET_DIR / file_path
            target.parent.mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构创建完成\n")

def operate_files():
    """执行文件操作"""
    print(f"📦 开始{OPERATION_TYPE}文件...\n")
    
    operated_count = 0
    not_found_count = 0
    error_count = 0
    
    for file_path in FILES_TO_OPERATE:
        source = BASE_DIR / file_path
        
        if not source.exists():
            print(f"  ⚠️  未找到：{file_path}")
            not_found_count += 1
            continue
        
        try:
            if OPERATION_TYPE == 'move':
                target = TARGET_DIR / file_path if KEEP_DIR_STRUCTURE else TARGET_DIR / source.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(target))
                print(f"  ✅ 已移动：{file_path}")
                
            elif OPERATION_TYPE == 'copy':
                target = TARGET_DIR / file_path if KEEP_DIR_STRUCTURE else TARGET_DIR / source.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(source), str(target))
                print(f"  ✅ 已复制：{file_path}")
                
            elif OPERATION_TYPE == 'delete':
                source.unlink()
                print(f"  ✅ 已删除：{file_path}")
            
            operated_count += 1
            
        except Exception as e:
            print(f"  ❌ 操作失败：{file_path} - {str(e)}")
            error_count += 1
    
    print(f"\n📊 操作统计：")
    print(f"  ✅ 成功{OPERATION_TYPE}：{operated_count} 个文件")
    print(f"  ⚠️  未找到：{not_found_count} 个文件")
    print(f"  ❌ 操作失败：{error_count} 个文件")
    print(f"  📋 总计：{len(FILES_TO_OPERATE)} 个文件")
    
    return operated_count, not_found_count, error_count

def main():
    """主函数"""
    print("=" * 60)
    print(f"📦 批量文件操作脚本（{OPERATION_TYPE}）")
    print("=" * 60)
    print()
    
    # 创建目录结构
    create_directories()
    
    # 执行文件操作
    operated_count, not_found_count, error_count = operate_files()
    
    print("\n" + "=" * 60)
    print("✅ 文件操作完成！")
    print("=" * 60)
    
    if operated_count > 0:
        print(f"\n✅ 成功{OPERATION_TYPE} {operated_count} 个文件")
    if not_found_count > 0:
        print(f"⚠️  有 {not_found_count} 个文件未找到（可能已删除）")
    if error_count > 0:
        print(f"❌ 有 {error_count} 个文件操作失败")

if __name__ == "__main__":
    main()

