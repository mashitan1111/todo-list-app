#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查代码中是否包含硬编码的 GitHub Token
"""
import os
import sys
import re

# 已知的 Token 前缀（用于检测）
TOKEN_PATTERN = r'ghp_[A-Za-z0-9]{36}'

def check_file_for_token(file_path):
    """检查单个文件是否包含 Token"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            matches = re.findall(TOKEN_PATTERN, content)
            if matches:
                return matches
    except Exception:
        pass
    return []

def scan_directory(directory):
    """扫描目录中的所有文件"""
    issues = []
    excluded_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
    excluded_extensions = {'.pyc', '.pyo', '.db', '.sqlite', '.log'}
    
    for root, dirs, files in os.walk(directory):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            # 排除特定扩展名
            if any(file.endswith(ext) for ext in excluded_extensions):
                continue
            
            file_path = os.path.join(root, file)
            matches = check_file_for_token(file_path)
            if matches:
                issues.append({
                    'file': file_path,
                    'tokens': matches
                })
    
    return issues

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("正在检查代码中的 Token 泄露...")
    issues = scan_directory(script_dir)
    
    if issues:
        print("\n✗ 发现以下文件包含硬编码的 Token：")
        for issue in issues:
            print(f"  - {issue['file']}")
            for token in issue['tokens']:
                print(f"    Token: {token[:10]}...")
        print("\n请先清理这些文件中的 Token，然后再提交代码。")
        return 1
    else:
        print("✓ 未发现硬编码的 Token")
        return 0

if __name__ == "__main__":
    sys.exit(main())

