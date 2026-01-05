#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件整理脚本 - 完整版
用途：整理cursor目录下的所有文件
创建日期：2026-01-04
版本：V1.0
"""

import os
import shutil
from pathlib import Path

# 基础目录
BASE_DIR = Path(__file__).parent.parent.parent
YUANXIN_DIR = BASE_DIR / "圆心工作"

# 整理规则
ORGANIZE_RULES = {
    # 根目录文件整理
    "root_files": {
        "工作流程详细版.txt": "圆心工作/文档资料/",
        "桌面整理提示词.txt": "圆心工作/文档资料/",
        "桌面整理方案.md": "圆心工作/文档资料/",
    },
    
    # 圆心工作目录下的散落文件整理
    "yuanxin_files": {
        # 工具文档类
        "AI Agent工具集成指南：Codaro与Skill工具.md": "圆心工作/工具文档/",
        "Skill Seeker使用指南.md": "圆心工作/工具文档/",
        "Skill Seeker安装验证报告.md": "圆心工作/工具文档/",
        "Skill Seeker技能包生成总结.md": "圆心工作/工具文档/",
        "技能包使用策略文档.md": "圆心工作/工具文档/",
        
        # 思考总结类
        "RAG思考与课程大纲设计_疑问与总结.md": "圆心工作/文档资料/",
        "rag思考以及课程大纲设计.txt": "圆心工作/文档资料/",
        "课程设计改变总结：RAG思考应用情况.md": "圆心工作/文档资料/",
        "课程设计深度分析：恐惧深植与异议粉碎机.md": "圆心工作/文档资料/",
        
        # 报告类
        "RAG知识库优化方案.md": "圆心工作/工作记录系统/",
        "公司业务与客户总结报告.md": "圆心工作/文档资料/",
        "内容连贯性与逻辑漏洞检查报告_2026-01-03.md": "圆心工作/工作记录系统/",
        
        # 工作记录类
        "工作完成记录.md": "圆心工作/工作记录系统/",
        
        # Word文档类
        "销售SOP库完整文档_高级目录版.docx": "圆心工作/输出文件/",
        "圆心销售SOP库完整文档.docx": "圆心工作/输出文件/",
    },
    
    # 文件夹整理
    "folders": {
        "Skill_Seekers": "圆心工作/工具和脚本/Skill_Seekers/",
        "杂乱文件": "圆心工作/文档资料/杂乱文件/",
    }
}

def create_directories():
    """创建必要的目录"""
    dirs_to_create = [
        "圆心工作/工具文档",
        "圆心工作/工具和脚本",
        "圆心工作/文档资料/杂乱文件",
    ]
    
    for dir_path in dirs_to_create:
        full_path = BASE_DIR / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 已创建目录: {dir_path}")

def move_file(src_path, dst_path):
    """移动文件"""
    try:
        if src_path.exists():
            # 确保目标目录存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 如果目标文件已存在，添加序号
            if dst_path.exists():
                base_name = dst_path.stem
                extension = dst_path.suffix
                counter = 1
                while dst_path.exists():
                    dst_path = dst_path.parent / f"{base_name}_{counter}{extension}"
                    counter += 1
            
            shutil.move(str(src_path), str(dst_path))
            print(f"✅ 已移动: {src_path.name} -> {dst_path}")
            return True
        else:
            print(f"⚠️ 文件不存在，跳过: {src_path}")
            return False
    except Exception as e:
        print(f"❌ 移动失败: {src_path.name} - {e}")
        return False

def move_folder(src_path, dst_path):
    """移动文件夹"""
    try:
        if src_path.exists() and src_path.is_dir():
            # 确保目标目录的父目录存在
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 如果目标文件夹已存在，合并内容
            if dst_path.exists():
                print(f"⚠️ 目标文件夹已存在，跳过: {dst_path}")
                return False
            
            shutil.move(str(src_path), str(dst_path))
            print(f"✅ 已移动文件夹: {src_path.name} -> {dst_path}")
            return True
        else:
            print(f"⚠️ 文件夹不存在，跳过: {src_path}")
            return False
    except Exception as e:
        print(f"❌ 移动文件夹失败: {src_path.name} - {e}")
        return False

def organize_root_files():
    """整理根目录文件"""
    print("\n" + "="*60)
    print("📁 开始整理根目录文件...")
    print("="*60)
    
    moved_count = 0
    for filename, target_dir in ORGANIZE_RULES["root_files"].items():
        src_path = BASE_DIR / filename
        dst_path = BASE_DIR / target_dir / filename
        
        if move_file(src_path, dst_path):
            moved_count += 1
    
    print(f"\n✅ 根目录文件整理完成，共移动 {moved_count} 个文件")
    return moved_count

def organize_yuanxin_files():
    """整理圆心工作目录下的散落文件"""
    print("\n" + "="*60)
    print("📁 开始整理圆心工作目录下的散落文件...")
    print("="*60)
    
    moved_count = 0
    for filename, target_dir in ORGANIZE_RULES["yuanxin_files"].items():
        src_path = YUANXIN_DIR / filename
        dst_path = BASE_DIR / target_dir / filename
        
        if move_file(src_path, dst_path):
            moved_count += 1
    
    print(f"\n✅ 圆心工作目录文件整理完成，共移动 {moved_count} 个文件")
    return moved_count

def organize_folders():
    """整理文件夹"""
    print("\n" + "="*60)
    print("📁 开始整理文件夹...")
    print("="*60)
    
    moved_count = 0
    for folder_name, target_dir in ORGANIZE_RULES["folders"].items():
        src_path = BASE_DIR / folder_name
        dst_path = BASE_DIR / target_dir
        
        if move_folder(src_path, dst_path):
            moved_count += 1
    
    print(f"\n✅ 文件夹整理完成，共移动 {moved_count} 个文件夹")
    return moved_count

def organize_tool_scripts():
    """整理工具脚本文件夹（如果存在）"""
    print("\n" + "="*60)
    print("📁 检查工具脚本文件夹...")
    print("="*60)
    
    tool_scripts_src = YUANXIN_DIR / "工具脚本"
    tool_scripts_dst = BASE_DIR / "圆心工作/工具和脚本/工具脚本"
    
    if tool_scripts_src.exists() and not tool_scripts_dst.exists():
        if move_folder(tool_scripts_src, tool_scripts_dst):
            print("✅ 工具脚本文件夹已移动到工具和脚本目录")
            return True
    else:
        print("ℹ️ 工具脚本文件夹已在正确位置或目标已存在")
        return False

def handle_encoding_issue_folder():
    """处理编码问题的文件夹（鍦嗗績宸ヤ綔）"""
    print("\n" + "="*60)
    print("📁 检查编码问题文件夹...")
    print("="*60)
    
    encoding_folder = BASE_DIR / "鍦嗗績宸ヤ綔"
    if encoding_folder.exists():
        print(f"⚠️ 发现编码问题文件夹: {encoding_folder}")
        print("   建议手动处理此文件夹（可能是圆心工作的编码问题版本）")
        print("   如果确认是重复内容，可以删除")
        return False
    else:
        print("✅ 未发现编码问题文件夹")
        return True

def generate_organize_report():
    """生成整理报告"""
    report = f"""
# 文件整理报告

## 整理时间
{Path(__file__).stat().st_mtime}

## 整理内容

### 1. 根目录文件整理
"""
    for filename, target_dir in ORGANIZE_RULES["root_files"].items():
        report += f"- {filename} -> {target_dir}\n"
    
    report += "\n### 2. 圆心工作目录文件整理\n"
    for filename, target_dir in ORGANIZE_RULES["yuanxin_files"].items():
        report += f"- {filename} -> {target_dir}\n"
    
    report += "\n### 3. 文件夹整理\n"
    for folder_name, target_dir in ORGANIZE_RULES["folders"].items():
        report += f"- {folder_name}/ -> {target_dir}\n"
    
    report_path = YUANXIN_DIR / "工作记录系统" / "文件整理报告_20260104.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"\n✅ 整理报告已生成: {report_path}")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 开始文件整理...")
    print("="*60)
    
    # 创建必要目录
    create_directories()
    
    # 整理文件
    root_count = organize_root_files()
    yuanxin_count = organize_yuanxin_files()
    folder_count = organize_folders()
    
    # 整理工具脚本
    organize_tool_scripts()
    
    # 处理编码问题文件夹
    handle_encoding_issue_folder()
    
    # 生成报告
    generate_organize_report()
    
    # 总结
    print("\n" + "="*60)
    print("✅ 文件整理完成！")
    print("="*60)
    print(f"📊 整理统计:")
    print(f"   - 根目录文件: {root_count} 个")
    print(f"   - 圆心工作文件: {yuanxin_count} 个")
    print(f"   - 文件夹: {folder_count} 个")
    print(f"   - 总计: {root_count + yuanxin_count + folder_count} 项")

if __name__ == "__main__":
    main()

