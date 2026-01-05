#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
归档旧版本文件脚本
用途：将逐字稿和Agent工作流程指南的旧版本文件移动到归档目录
"""

import os
import shutil
from pathlib import Path

# 工作目录
BASE_DIR = Path(__file__).parent.parent / "RAG知识库"

def archive_transcript_old_versions():
    """归档逐字稿旧版本"""
    print("=" * 60)
    print("开始归档逐字稿旧版本...")
    print("=" * 60)
    
    # Day1旧版本文件
    day1_files = [
        "04_直播课程库/Day1_破冰归因/02_完整逐字稿_内部版.md",
        "04_直播课程库/Day1_破冰归因/02_完整逐字稿_新版_V2.0.md",
        "04_直播课程库/Day1_破冰归因/02_完整逐字稿_超级完整版_V3.0DAY1.md",
    ]
    
    # Day2旧版本文件
    day2_files = [
        "04_直播课程库/Day2_核心逼单/02_完整逐字稿_新版_V2.0.md",
        "04_直播课程库/Day2_核心逼单/02_完整逐字稿_超级完整版_V3.0DAY2.md",
    ]
    
    # Day3旧版本文件
    day3_files = [
        "04_直播课程库/Day3_答疑清尾/02_完整逐字稿_新版_V2.0.md",
        "04_直播课程库/Day3_答疑清尾/02_完整逐字稿_超级完整版_V3.0DAY3.md",
    ]
    
    # 归档目录
    archive_dirs = {
        "day1": BASE_DIR / "04_直播课程库/归档文件/Day1_旧版本",
        "day2": BASE_DIR / "04_直播课程库/归档文件/Day2_旧版本",
        "day3": BASE_DIR / "04_直播课程库/归档文件/Day3_旧版本",
    }
    
    # 创建归档目录
    for archive_dir in archive_dirs.values():
        archive_dir.mkdir(parents=True, exist_ok=True)
    
    # 移动Day1文件
    moved_count = 0
    for file_path in day1_files:
        src = BASE_DIR / file_path
        if src.exists():
            dst = archive_dirs["day1"] / src.name
            try:
                shutil.move(str(src), str(dst))
                print(f"✅ 已移动: {src.name} -> {dst}")
                moved_count += 1
            except Exception as e:
                print(f"❌ 移动失败: {src.name} - {e}")
    
    # 移动Day2文件
    for file_path in day2_files:
        src = BASE_DIR / file_path
        if src.exists():
            dst = archive_dirs["day2"] / src.name
            try:
                shutil.move(str(src), str(dst))
                print(f"✅ 已移动: {src.name} -> {dst}")
                moved_count += 1
            except Exception as e:
                print(f"❌ 移动失败: {src.name} - {e}")
    
    # 移动Day3文件
    for file_path in day3_files:
        src = BASE_DIR / file_path
        if src.exists():
            dst = archive_dirs["day3"] / src.name
            try:
                shutil.move(str(src), str(dst))
                print(f"✅ 已移动: {src.name} -> {dst}")
                moved_count += 1
            except Exception as e:
                print(f"❌ 移动失败: {src.name} - {e}")
    
    print(f"\n✅ 逐字稿归档完成，共移动 {moved_count} 个文件")
    return moved_count


def archive_agent_guide_old_versions():
    """归档Agent工作流程指南旧版本"""
    print("\n" + "=" * 60)
    print("开始归档Agent工作流程指南旧版本...")
    print("=" * 60)
    
    # 旧版本文件
    old_files = [
        "Agent工作流程指南/00_Agent工作流程总指南.md",
        "Agent工作流程指南/01_每日工作流程SOP.md",
    ]
    
    # 归档目录
    archive_dir = BASE_DIR / "Agent工作流程指南/归档文件"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    # 移动文件
    moved_count = 0
    for file_path in old_files:
        src = BASE_DIR / file_path
        if src.exists():
            dst = archive_dir / src.name
            try:
                shutil.move(str(src), str(dst))
                print(f"✅ 已移动: {src.name} -> {dst}")
                moved_count += 1
            except Exception as e:
                print(f"❌ 移动失败: {src.name} - {e}")
    
    print(f"\n✅ Agent工作流程指南归档完成，共移动 {moved_count} 个文件")
    return moved_count


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("旧版本文件归档脚本")
    print("=" * 60)
    print(f"工作目录: {BASE_DIR}")
    print()
    
    # 归档逐字稿旧版本
    transcript_count = archive_transcript_old_versions()
    
    # 归档Agent工作流程指南旧版本
    agent_count = archive_agent_guide_old_versions()
    
    # 总结
    print("\n" + "=" * 60)
    print("归档完成总结")
    print("=" * 60)
    print(f"逐字稿旧版本: {transcript_count} 个文件")
    print(f"Agent工作流程指南旧版本: {agent_count} 个文件")
    print(f"总计: {transcript_count + agent_count} 个文件")
    print("\n✅ 所有旧版本文件已归档完成！")


if __name__ == "__main__":
    main()

