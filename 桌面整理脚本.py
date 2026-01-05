#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
桌面文件整理脚本
用途：整理桌面上的散落文件到对应文件夹
"""

import os
import shutil
from pathlib import Path

# 桌面路径
DESKTOP = Path.home() / "Desktop"

# 整理规则
ORGANIZE_RULES = {
    # 临时文件（删除）
    "delete_files": [
        "~$三天直播数据剔除版.xlsx",
        "~$思路.docx",
        "~$成人子女教育_销售核心数据复盘表_优化版.xlsx",
        "~$成人子女教育_高阶课程销售作战地图.xlsx",
        "~$成人子女教育销售跟踪可视化表.xlsx",
        "~$绩效考核标准_AI赋能版_精美版.docx",
        "~$销售SOP库完整全量版_精美Excel.xlsx",
        "~$销售绩效考核标准_AI赋能全量版_精美Excel.xlsx",
        "~$销售绩效考核标准_AI赋能版_精美Excel.xlsx",
    ],
    
    # 文本文件 -> 文档资料/文本文件/
    "text_files": {
        "11.txt": "文档资料/文本文件/",
        "999.txt": "文档资料/文本文件/",
        "rag思考以及课程大纲设计.txt": "文档资料/文本文件/",
        "填表客户状态分析.txt": "文档资料/文本文件/",
    },
    
    # Excel文件 -> 文档资料/Excel表格/
    "excel_files": {
        "销售SOP库完整全量版_精美Excel.xlsx": "文档资料/Excel表格/",
        "销售绩效考核标准_AI赋能全量版_精美Excel.xlsx": "文档资料/Excel表格/",
        "销售绩效考核标准_AI赋能版_精美Excel.xlsx": "文档资料/Excel表格/",
    },
    
    # Word文件 -> 文档资料/Word文档/
    "word_files": {
        "销售绩效考核标准_AI赋能版_精美版.docx": "文档资料/Word文档/",
    },
}

def create_directories():
    """创建必要的目录"""
    dirs = [
        "文档资料/文本文件",
        "文档资料/Excel表格",
        "文档资料/Word文档",
    ]
    
    for dir_path in dirs:
        full_path = DESKTOP / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录：{full_path}")

def delete_temp_files():
    """删除临时文件"""
    deleted_count = 0
    for file_name in ORGANIZE_RULES["delete_files"]:
        file_path = DESKTOP / file_name
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"🗑️  删除临时文件：{file_name}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ 删除失败 {file_name}：{e}")
    return deleted_count

def move_files(category, dest_base):
    """移动文件到指定目录"""
    moved_count = 0
    for file_name, dest_path_str in ORGANIZE_RULES[category].items():
        src_path = DESKTOP / file_name
        dest_path = DESKTOP / dest_path_str / file_name
        
        if src_path.exists():
            try:
                # 如果目标文件已存在，添加序号
                if dest_path.exists():
                    base_name = dest_path.stem
                    ext = dest_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = dest_path.parent / f"{base_name}_{counter}{ext}"
                        counter += 1
                
                shutil.move(str(src_path), str(dest_path))
                print(f"📦 移动文件：{file_name} -> {dest_path_str}")
                moved_count += 1
            except Exception as e:
                print(f"❌ 移动失败 {file_name}：{e}")
        else:
            print(f"⚠️  文件不存在：{file_name}")
    
    return moved_count

def main():
    print("=" * 50)
    print("🚀 开始整理桌面文件...")
    print("=" * 50)
    
    # 创建目录
    create_directories()
    print()
    
    # 删除临时文件
    print("📋 删除临时文件...")
    deleted = delete_temp_files()
    print(f"✅ 已删除 {deleted} 个临时文件\n")
    
    # 移动文本文件
    print("📋 移动文本文件...")
    text_moved = move_files("text_files", "文档资料/文本文件/")
    print(f"✅ 已移动 {text_moved} 个文本文件\n")
    
    # 移动Excel文件
    print("📋 移动Excel文件...")
    excel_moved = move_files("excel_files", "文档资料/Excel表格/")
    print(f"✅ 已移动 {excel_moved} 个Excel文件\n")
    
    # 移动Word文件
    print("📋 移动Word文件...")
    word_moved = move_files("word_files", "文档资料/Word文档/")
    print(f"✅ 已移动 {word_moved} 个Word文件\n")
    
    print("=" * 50)
    print("✅ 桌面文件整理完成！")
    print("=" * 50)
    print(f"📊 统计：")
    print(f"   - 删除临时文件：{deleted} 个")
    print(f"   - 移动文本文件：{text_moved} 个")
    print(f"   - 移动Excel文件：{excel_moved} 个")
    print(f"   - 移动Word文件：{word_moved} 个")

if __name__ == "__main__":
    main()

