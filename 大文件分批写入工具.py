#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
大文件分批写入工具
用途：解决大文件一次性写入导致超时的问题
创建日期：2026-01-04
版本：V1.0
"""

import os
from pathlib import Path
from typing import Optional


def write_file_in_batches(file_path: str, content: str, batch_size: int = 1000, max_retries: int = 3) -> bool:
    """
    分批写入大文件
    
    参数:
        file_path: 文件路径
        content: 文件内容
        batch_size: 每批写入的最大字符数（默认1000）
        max_retries: 最大重试次数（默认3）
    
    返回:
        bool: 是否成功写入
    """
    # 如果内容小于等于batch_size，直接写入
    if len(content) <= batch_size:
        return _write_file_directly(file_path, content, max_retries)
    
    # 创建文件目录（如果不存在）
    file_path_obj = Path(file_path)
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # 分批写入
    try:
        # 如果文件已存在，先删除
        if file_path_obj.exists():
            file_path_obj.unlink()
        
        # 分批写入
        total_chars = len(content)
        written_chars = 0
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for i in range(0, total_chars, batch_size):
                batch = content[i:i + batch_size]
                f.write(batch)
                written_chars += len(batch)
                
                # 每批写入后刷新缓冲区
                f.flush()
        
        # 验证文件
        if _verify_file(file_path, content):
            print(f"✅ 文件写入成功: {file_path} (总字符数: {total_chars}, 批次数: {(total_chars + batch_size - 1) // batch_size})")
            return True
        else:
            print(f"❌ 文件验证失败: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 文件写入失败: {file_path}, 错误: {e}")
        # 重试
        for retry in range(max_retries):
            try:
                if _write_file_directly(file_path, content, 1):
                    if _verify_file(file_path, content):
                        print(f"✅ 文件写入成功（重试 {retry + 1} 次）: {file_path}")
                        return True
            except Exception as retry_error:
                print(f"⚠️ 重试 {retry + 1} 次失败: {retry_error}")
        
        return False


def _write_file_directly(file_path: str, content: str, max_retries: int = 3) -> bool:
    """
    直接写入文件（小文件或重试时使用）
    """
    file_path_obj = Path(file_path)
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    for retry in range(max_retries):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            if retry < max_retries - 1:
                print(f"⚠️ 写入失败，重试 {retry + 1}/{max_retries}: {e}")
            else:
                print(f"❌ 写入失败（已重试 {max_retries} 次）: {e}")
                return False
    
    return False


def _verify_file(file_path: str, expected_content: str) -> bool:
    """
    验证文件是否存在且内容完整
    """
    try:
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            actual_content = f.read()
        
        return actual_content == expected_content
    except Exception as e:
        print(f"⚠️ 文件验证出错: {e}")
        return False


def append_to_file_in_batches(file_path: str, content: str, batch_size: int = 1000) -> bool:
    """
    分批追加内容到文件
    
    参数:
        file_path: 文件路径
        content: 要追加的内容
        batch_size: 每批写入的最大字符数（默认1000）
    
    返回:
        bool: 是否成功追加
    """
    file_path_obj = Path(file_path)
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # 如果内容小于等于batch_size，直接追加
        if len(content) <= batch_size:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
                f.flush()
            return True
        
        # 分批追加
        total_chars = len(content)
        with open(file_path, 'a', encoding='utf-8') as f:
            for i in range(0, total_chars, batch_size):
                batch = content[i:i + batch_size]
                f.write(batch)
                f.flush()
        
        print(f"✅ 内容追加成功: {file_path} (追加字符数: {total_chars})")
        return True
        
    except Exception as e:
        print(f"❌ 内容追加失败: {file_path}, 错误: {e}")
        return False


# 使用示例
if __name__ == "__main__":
    # 示例1：写入大文件
    test_content = "这是一个测试内容。" * 500  # 生成大约5000字的内容
    test_file = r"C:\Users\温柔的男子啊\Desktop\crusor\圆心工作\测试文件_分批写入.txt"
    
    print("=" * 60)
    print("大文件分批写入工具测试")
    print("=" * 60)
    print(f"文件路径: {test_file}")
    print(f"内容长度: {len(test_content)} 字符")
    print()
    
    # 写入文件
    success = write_file_in_batches(test_file, test_content, batch_size=1000)
    
    if success:
        print("✅ 测试通过！")
    else:
        print("❌ 测试失败！")
    
    print("=" * 60)

