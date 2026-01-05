#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
移动待删除文件脚本
用途：将建议删除的文件移动到"待删除文件"文件夹
"""

import os
import shutil
from pathlib import Path

# 基础目录
BASE_DIR = Path(__file__).parent.parent

# 待删除文件目录
DELETE_DIR = BASE_DIR / "待删除文件"

# 待删除文件列表
FILES_TO_DELETE = {
    # P0级别：备份文件（已迁移到Skill库）
    "工作记录系统/需求理解模板.md": "工作记录系统/需求理解模板.md",
    "工作记录系统/内容生成模板.md": "工作记录系统/内容生成模板.md",
    "工作记录系统/质量检查清单.md": "工作记录系统/质量检查清单.md",
    "工作记录系统/工作流程优化方案_V3.0.md": "工作记录系统/工作流程优化方案_V3.0.md",
    
    # P0级别：旧版本检查报告
    "工作记录系统/RAG知识库质量检查报告_20260103.md": "工作记录系统/RAG知识库质量检查报告_20260103.md",
    "RAG知识库/RAG知识库完整检查报告_2026-01-03.md": "RAG知识库/RAG知识库完整检查报告_2026-01-03.md",
    "RAG知识库/RAG知识库全面问题检查报告_2026-01-03.md": "RAG知识库/RAG知识库全面问题检查报告_2026-01-03.md",
    "RAG知识库/业务逻辑全面检查报告_2026-01-03.md": "RAG知识库/业务逻辑全面检查报告_2026-01-03.md",
    "内容连贯性与逻辑漏洞检查报告_2026-01-03.md": "内容连贯性与逻辑漏洞检查报告_2026-01-03.md",
    "RAG知识库/RAG知识库重大问题检查报告.md": "RAG知识库/RAG知识库重大问题检查报告.md",
    
    # P0级别：旧版本工作流程指南
    "RAG知识库/Agent工作流程指南/00_Agent工作流程总指南.md": "RAG知识库/Agent工作流程指南/00_Agent工作流程总指南.md",
    "RAG知识库/Agent工作流程指南/01_每日工作流程SOP.md": "RAG知识库/Agent工作流程指南/01_每日工作流程SOP.md",
    
    # P0级别：逐字稿旧版本
    "RAG知识库/04_直播课程库/Day1_破冰归因/02_完整逐字稿_内部版.md": "RAG知识库/04_直播课程库/Day1_破冰归因/02_完整逐字稿_内部版.md",
    "RAG知识库/04_直播课程库/Day1_破冰归因/02_完整逐字稿_新版_V2.0.md": "RAG知识库/04_直播课程库/Day1_破冰归因/02_完整逐字稿_新版_V2.0.md",
    "RAG知识库/04_直播课程库/Day1_破冰归因/02_完整逐字稿_超级完整版_V3.0DAY1.md": "RAG知识库/04_直播课程库/Day1_破冰归因/02_完整逐字稿_超级完整版_V3.0DAY1.md",
    "RAG知识库/04_直播课程库/Day2_核心逼单/02_完整逐字稿_新版_V2.0.md": "RAG知识库/04_直播课程库/Day2_核心逼单/02_完整逐字稿_新版_V2.0.md",
    "RAG知识库/04_直播课程库/Day2_核心逼单/02_完整逐字稿_超级完整版_V3.0DAY2.md": "RAG知识库/04_直播课程库/Day2_核心逼单/02_完整逐字稿_超级完整版_V3.0DAY2.md",
    "RAG知识库/04_直播课程库/Day3_答疑清尾/02_完整逐字稿_新版_V2.0.md": "RAG知识库/04_直播课程库/Day3_答疑清尾/02_完整逐字稿_新版_V2.0.md",
    "RAG知识库/04_直播课程库/Day3_答疑清尾/02_完整逐字稿_超级完整版_V3.0DAY3.md": "RAG知识库/04_直播课程库/Day3_答疑清尾/02_完整逐字稿_超级完整版_V3.0DAY3.md",
    
    # P1级别：测试和演示文件
    "工作记录系统/工作方式优化系统测试报告.md": "工作记录系统/工作方式优化系统测试报告.md",
    "工作记录系统/工具使用演示.md": "工作记录系统/工具使用演示.md",
    "工作记录系统/自动化脚本使用演示.md": "工作记录系统/自动化脚本使用演示.md",
    "工作记录系统/自动化脚本实战演示.md": "工作记录系统/自动化脚本实战演示.md",
    "工作记录系统/自动化脚本演示总结.md": "工作记录系统/自动化脚本演示总结.md",
    
    # P1级别：重复的完成报告
    "工作记录系统/P1任务处理完成报告.md": "工作记录系统/P1任务处理完成报告.md",
    "工作记录系统/RAG知识库质量提升完成报告.md": "工作记录系统/RAG知识库质量提升完成报告.md",
    "工作记录系统/RAG知识库P1P2级别问题处理完成报告.md": "工作记录系统/RAG知识库P1P2级别问题处理完成报告.md",
    
    # P1级别：旧版本的修复报告
    "RAG知识库/修复完成报告_2026-01-03.md": "RAG知识库/修复完成报告_2026-01-03.md",
    "RAG知识库/修复进度报告_2026-01-03.md": "RAG知识库/修复进度报告_2026-01-03.md",
    "RAG知识库/优化修复完成报告_2026-01-03.md": "RAG知识库/优化修复完成报告_2026-01-03.md",
    
    # P2级别：其他完成报告
    "工作记录系统/优化方案实施进度报告.md": "工作记录系统/优化方案实施进度报告.md",
    "工作记录系统/第二阶段实施完成报告.md": "工作记录系统/第二阶段实施完成报告.md",
    "工作记录系统/优化工具创建完成报告.md": "工作记录系统/优化工具创建完成报告.md",
    "工作记录系统/工作方式优化集成完成报告.md": "工作记录系统/工作方式优化集成完成报告.md",
    "工作记录系统/RAG知识库版本冲突处理报告.md": "工作记录系统/RAG知识库版本冲突处理报告.md",
    "工作记录系统/RAG知识库持续优化机制.md": "工作记录系统/RAG知识库持续优化机制.md",
}

def create_directories():
    """创建必要的目录结构"""
    print("📁 创建目录结构...")
    
    # 创建主目录
    DELETE_DIR.mkdir(exist_ok=True)
    
    # 创建子目录
    subdirs = [
        "工作记录系统",
        "RAG知识库",
        "RAG知识库/Agent工作流程指南",
        "RAG知识库/04_直播课程库",
        "RAG知识库/04_直播课程库/Day1_破冰归因",
        "RAG知识库/04_直播课程库/Day2_核心逼单",
        "RAG知识库/04_直播课程库/Day3_答疑清尾",
    ]
    
    for subdir in subdirs:
        dir_path = DELETE_DIR / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {subdir}")
    
    print("✅ 目录结构创建完成\n")

def move_files():
    """移动文件到待删除文件夹"""
    print("📦 开始移动文件...\n")
    
    moved_count = 0
    not_found_count = 0
    error_count = 0
    
    for source_path, target_path in FILES_TO_DELETE.items():
        source = BASE_DIR / source_path
        target = DELETE_DIR / target_path
        
        if not source.exists():
            print(f"  ⚠️  未找到：{source_path}")
            not_found_count += 1
            continue
        
        try:
            # 确保目标目录存在
            target.parent.mkdir(parents=True, exist_ok=True)
            
            # 移动文件
            shutil.move(str(source), str(target))
            print(f"  ✅ 已移动：{source_path}")
            moved_count += 1
        except Exception as e:
            print(f"  ❌ 移动失败：{source_path} - {str(e)}")
            error_count += 1
    
    print(f"\n📊 移动统计：")
    print(f"  ✅ 成功移动：{moved_count} 个文件")
    print(f"  ⚠️  未找到：{not_found_count} 个文件")
    print(f"  ❌ 移动失败：{error_count} 个文件")
    print(f"  📋 总计：{len(FILES_TO_DELETE)} 个文件")

def create_readme():
    """创建README说明文件"""
    readme_content = """# 待删除文件

## 【说明】
此文件夹包含建议删除的文件，已从原位置移动到此文件夹。

## 【删除建议】
1. **先检查**：确认文件已不再需要
2. **再删除**：确认后可以删除整个文件夹
3. **保留备份**：如果需要，可以先备份重要文件

## 【文件分类】
- P0级别：17个文件（强烈建议删除）
- P1级别：8个文件（可以删除）
- P2级别：6个文件（可选删除）

## 【详细清单】
请查看：`工作记录系统/建议删除文件清单.md`

---
**创建时间**：2026-01-04
"""
    
    readme_path = DELETE_DIR / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"\n📝 已创建README：{readme_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("📦 移动待删除文件脚本")
    print("=" * 60)
    print()
    
    # 创建目录结构
    create_directories()
    
    # 移动文件
    move_files()
    
    # 创建README
    create_readme()
    
    print("\n" + "=" * 60)
    print("✅ 文件移动完成！")
    print("=" * 60)
    print(f"\n📁 待删除文件位置：{DELETE_DIR}")
    print("💡 建议：检查文件后，确认不再需要再删除整个文件夹")

if __name__ == "__main__":
    main()

