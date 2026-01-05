#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件契合度优化脚本
用途：处理P0级别优化任务
创建日期：2026-01-04
版本：V1.0
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# 基础目录
BASE_DIR = Path(__file__).parent.parent

def archive_old_versions():
    """归档旧版本文件"""
    print("=" * 60)
    print("开始归档旧版本文件...")
    print("=" * 60)
    
    # 旧版本文件列表
    old_files = [
        "RAG知识库/Agent工作流程指南/00_Agent工作流程总指南.md",
        "RAG知识库/Agent工作流程指南/01_每日工作流程SOP.md",
    ]
    
    # 归档目录
    archive_dir = BASE_DIR / "RAG知识库/Agent工作流程指南/归档文件"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    for file_path in old_files:
        src = BASE_DIR / file_path
        if src.exists():
            dst = archive_dir / src.name
            try:
                shutil.move(str(src), str(dst))
                print(f"✅ 已归档: {src.name} -> {dst}")
                moved_count += 1
            except Exception as e:
                print(f"❌ 归档失败: {src.name} - {e}")
    
    print(f"\n✅ 归档完成，共归档 {moved_count} 个文件")
    return moved_count

def delete_duplicate_templates():
    """删除重复模板文件"""
    print("\n" + "=" * 60)
    print("开始删除重复模板文件...")
    print("=" * 60)
    
    # 重复文件列表（工作记录系统中的，已迁移到Skill库）
    duplicate_files = [
        "工作记录系统/内容生成模板.md",
        "工作记录系统/质量检查清单.md",
    ]
    
    deleted_count = 0
    for file_path in duplicate_files:
        src = BASE_DIR / file_path
        if src.exists():
            try:
                src.unlink()
                print(f"✅ 已删除: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ 删除失败: {file_path} - {e}")
    
    print(f"\n✅ 删除完成，共删除 {deleted_count} 个文件")
    return deleted_count

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("文件契合度优化脚本")
    print("=" * 60)
    print(f"工作目录: {BASE_DIR}")
    print()
    
    # 归档旧版本文件
    archive_count = archive_old_versions()
    
    # 删除重复模板文件
    delete_count = delete_duplicate_templates()
    
    # 总结
    print("\n" + "=" * 60)
    print("优化完成总结")
    print("=" * 60)
    print(f"归档旧版本: {archive_count} 个文件")
    print(f"删除重复文件: {delete_count} 个文件")
    print(f"总计: {archive_count + delete_count} 个文件")
    print("\n✅ 所有优化任务已完成！")

if __name__ == "__main__":
    main()

