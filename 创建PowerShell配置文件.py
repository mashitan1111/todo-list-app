#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建 PowerShell 配置文件
用途：自动创建 PowerShell 配置文件，设置 UTF-8 编码
"""

import os
from pathlib import Path

# PowerShell 配置文件路径
profile_path = Path.home() / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"

# 配置文件内容
profile_content = """# PowerShell 配置文件 - UTF-8 编码设置
# 此文件会在每次 PowerShell 启动时自动执行

# 设置控制台编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# 设置代码页为 65001 (UTF-8)
chcp 65001 | Out-Null

# 设置 PowerShell 默认编码
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

# 显示编码设置成功信息（可选，可以注释掉）
# Write-Host "UTF-8 编码已设置" -ForegroundColor Green
"""

def main():
    print("=" * 50)
    print("创建 PowerShell 配置文件...")
    print("=" * 50)
    
    # 创建目录（如果不存在）
    profile_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"✅ 目录已创建：{profile_path.parent}")
    
    # 检查文件是否已存在
    if profile_path.exists():
        print(f"⚠️  配置文件已存在：{profile_path}")
        response = input("是否覆盖？(y/n): ")
        if response.lower() != 'y':
            print("❌ 已取消")
            return
    
    # 写入配置文件
    try:
        with open(profile_path, 'w', encoding='utf-8') as f:
            f.write(profile_content)
        print(f"✅ 配置文件已创建：{profile_path}")
        print("\n📋 配置内容：")
        print("- UTF-8 编码设置")
        print("- 代码页 65001")
        print("- PowerShell 默认编码")
        print("\n⚠️  重要提示：")
        print("1. 请重启 Cursor 以使配置生效")
        print("2. 如果 PowerShell 执行策略限制，请运行：")
        print("   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
    except Exception as e:
        print(f"❌ 创建失败：{e}")

if __name__ == "__main__":
    main()


