# -*- coding: utf-8 -*-
"""
文件整理和清理计划执行脚本
按照计划执行所有清理任务
"""
import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent  # crusor目录
YUANXIN_DIR = BASE_DIR / "圆心工作"

def delete_directory(dir_path):
    """删除目录"""
    try:
        dir_path = Path(dir_path)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"✅ 已删除目录: {dir_path}")
            return True
        else:
            print(f"⚠️ 目录不存在: {dir_path}")
            return False
    except Exception as e:
        print(f"❌ 删除目录失败 {dir_path}: {e}")
        return False

def move_file(src, dst):
    """移动文件"""
    try:
        src, dst = Path(src), Path(dst)
        if not src.exists():
            print(f"⚠️ 源文件不存在: {src}")
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            if src.stat().st_size == dst.stat().st_size:
                print(f"⚠️ 目标文件已存在且大小相同，跳过: {dst}")
                src.unlink()  # 删除源文件
                return True
            else:
                backup = dst.with_suffix(dst.suffix + ".backup")
                shutil.copy2(dst, backup)
                print(f"   已备份现有文件到: {backup}")
        shutil.move(str(src), str(dst))
        print(f"✅ 已移动: {src.name} → {dst}")
        return True
    except Exception as e:
        print(f"❌ 移动文件失败 {src} → {dst}: {e}")
        return False

def move_directory_contents(src, dst):
    """移动目录内容到目标目录"""
    try:
        src, dst = Path(src), Path(dst)
        if not src.exists():
            print(f"⚠️ 源目录不存在: {src}")
            return False
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            dst_item = dst / item.name
            if item.is_dir():
                if dst_item.exists():
                    move_directory_contents(item, dst_item)
                    item.rmdir()
                else:
                    shutil.move(str(item), str(dst_item))
                    print(f"✅ 已移动目录: {item.name} → {dst_item}")
            else:
                move_file(item, dst_item)
        if src.exists() and not any(src.iterdir()):
            src.rmdir()
            print(f"✅ 已删除空目录: {src}")
        return True
    except Exception as e:
        print(f"❌ 移动目录内容失败 {src} → {dst}: {e}")
        return False

def create_directory(dir_path):
    """创建目录"""
    try:
        dir_path = Path(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 已创建目录: {dir_path}")
        return True
    except Exception as e:
        print(f"❌ 创建目录失败 {dir_path}: {e}")
        return False

def main():
    print("=" * 60)
    print("文件整理和清理计划执行")
    print("=" * 60)
    print()
    
    # 任务1：删除编码问题目录
    print("【任务1】删除编码问题目录")
    print("-" * 60)
    encoding_dir = BASE_DIR / "鍦嗗績宸ヤ綔"
    delete_directory(encoding_dir)
    print()
    
    # 任务2：完成工具脚本目录迁移
    print("【任务2】完成工具脚本目录迁移")
    print("-" * 60)
    src_script_dir = YUANXIN_DIR / "工具脚本"
    dst_script_dir = YUANXIN_DIR / "工具和脚本" / "工具脚本"
    if src_script_dir.exists():
        for item in src_script_dir.iterdir():
            dst_item = dst_script_dir / item.name
            if item.is_file():
                move_file(item, dst_item)
            elif item.is_dir():
                if dst_item.exists():
                    move_directory_contents(item, dst_item)
                else:
                    shutil.move(str(item), str(dst_item))
                    print(f"✅ 已移动目录: {item.name}")
        if src_script_dir.exists() and not any(src_script_dir.iterdir()):
            src_script_dir.rmdir()
            print(f"✅ 已删除空目录: {src_script_dir}")
    else:
        print(f"⚠️ 源目录不存在: {src_script_dir}")
    print()
    
    # 任务3：删除重复的README文件
    print("【任务3】删除重复的README文件")
    print("-" * 60)
    archive_delete_dir = YUANXIN_DIR / "归档文件" / "待删除文件"
    create_directory(archive_delete_dir)
    
    files_to_archive = [
        (YUANXIN_DIR / "归档文件" / "README_文件结构.md", archive_delete_dir / "README_文件结构.md"),
        (YUANXIN_DIR / "归档文件" / "文件整理说明.md", archive_delete_dir / "文件整理说明.md"),
    ]
    for src, dst in files_to_archive:
        if src.exists():
            move_file(src, dst)
    print()
    
    # 任务4：整理根目录散落文件
    print("【任务4】整理根目录散落文件")
    print("-" * 60)
    root_files = {
        BASE_DIR / "generate_word.py": YUANXIN_DIR / "工具和脚本" / "工具脚本" / "generate_word.py",
        BASE_DIR / "generate_advanced_word.py": YUANXIN_DIR / "工具和脚本" / "工具脚本" / "generate_advanced_word.py",
        BASE_DIR / "11.txt": YUANXIN_DIR / "文档资料" / "11.txt",
        BASE_DIR / "example.docx": YUANXIN_DIR / "文档资料" / "example.docx",
        BASE_DIR / "advanced_example.docx": YUANXIN_DIR / "文档资料" / "advanced_example.docx",
        BASE_DIR / "销售SOP库完整文档_优化版.docx": YUANXIN_DIR / "输出文件" / "销售SOP库完整文档_优化版.docx",
        BASE_DIR / "销售SOP库完整全量版_精美Excel.xlsx": YUANXIN_DIR / "输出文件" / "销售SOP库完整全量版_精美Excel.xlsx",
        BASE_DIR / "运行编码测试.bat": YUANXIN_DIR / "工具和脚本" / "运行编码测试.bat",
    }
    for src, dst in root_files.items():
        if src.exists():
            move_file(src, dst)
    print()
    
    # 任务5：处理杂乱文件目录
    print("【任务5】处理杂乱文件目录")
    print("-" * 60)
    misc_src = BASE_DIR / "杂乱文件"
    misc_dst = YUANXIN_DIR / "文档资料" / "杂乱文件"
    if misc_src.exists():
        move_directory_contents(misc_src, misc_dst)
    else:
        print(f"⚠️ 源目录不存在: {misc_src}")
    print()
    
    print("=" * 60)
    print("P0级别任务完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()

