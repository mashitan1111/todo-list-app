#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
编码测试脚本
用途：测试 PowerShell 编码修复是否成功
"""

import os
import sys
from pathlib import Path

def test_chinese_output():
    """测试中文输出"""
    print("=" * 50)
    print("测试 1: 中文输出")
    print("=" * 50)
    try:
        print("✅ 测试中文：你好世界")
        print("✅ 测试路径：C:\\Users\\温柔的男子啊\\Desktop\\crusor")
        return True
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False

def test_chinese_path():
    """测试中文路径读取"""
    print("\n" + "=" * 50)
    print("测试 2: 中文路径读取")
    print("=" * 50)
    try:
        test_path = Path.home() / "Desktop" / "crusor" / "圆心工作"
        if test_path.exists():
            print(f"✅ 路径存在：{test_path}")
            files = list(test_path.iterdir())[:3]  # 只显示前3个
            print(f"✅ 找到 {len(list(test_path.iterdir()))} 个文件/文件夹")
            for f in files:
                print(f"   - {f.name}")
            return True
        else:
            print(f"⚠️  路径不存在：{test_path}")
            return False
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False

def test_file_operations():
    """测试文件操作"""
    print("\n" + "=" * 50)
    print("测试 3: 文件操作")
    print("=" * 50)
    try:
        test_file = Path.home() / "Desktop" / "crusor" / "测试文件_中文.txt"
        # 创建测试文件
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("这是测试文件\n测试中文编码\n")
        print(f"✅ 创建文件成功：{test_file.name}")
        
        # 读取测试文件
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ 读取文件成功：{content.strip()}")
        
        # 删除测试文件
        test_file.unlink()
        print(f"✅ 删除文件成功")
        return True
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False

def check_encoding():
    """检查编码设置"""
    print("\n" + "=" * 50)
    print("测试 4: 编码检查")
    print("=" * 50)
    try:
        print(f"✅ Python 默认编码：{sys.getdefaultencoding()}")
        print(f"✅ 文件系统编码：{sys.getfilesystemencoding()}")
        print(f"✅ 标准输出编码：{sys.stdout.encoding}")
        return True
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False

def main():
    print("\n" + "🚀" * 25)
    print("PowerShell 编码修复验证测试")
    print("🚀" * 25 + "\n")
    
    results = []
    results.append(("中文输出", test_chinese_output()))
    results.append(("中文路径", test_chinese_path()))
    results.append(("文件操作", test_file_operations()))
    results.append(("编码检查", check_encoding()))
    
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！编码修复成功！")
    else:
        print("⚠️  部分测试失败，请检查配置")
    print("=" * 50)

if __name__ == "__main__":
    main()


