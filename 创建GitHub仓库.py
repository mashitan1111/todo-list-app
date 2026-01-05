#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动创建 GitHub 仓库（如果不存在）
"""
import os
import sys
import requests

def check_repo_exists(token, username, repo_name):
    """检查仓库是否存在"""
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

def create_repo(token, username, repo_name):
    """创建 GitHub 仓库"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    url = "https://api.github.com/user/repos"
    data = {
        "name": repo_name,
        "description": "Todo List App for Vercel",
        "private": False,
        "auto_init": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.status_code == 201
    except Exception:
        return False

def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("✗ 错误: GITHUB_TOKEN 环境变量未设置")
        return 1
    
    username = "mashitan1111"
    repo_name = "todo-list-app"
    
    # 检查仓库是否存在
    if check_repo_exists(token, username, repo_name):
        print(f"✓ 仓库 {username}/{repo_name} 已存在")
        return 0
    
    # 创建仓库
    print(f"正在创建仓库 {username}/{repo_name}...")
    if create_repo(token, username, repo_name):
        print(f"✓ 仓库创建成功: https://github.com/{username}/{repo_name}")
        return 0
    else:
        print(f"✗ 仓库创建失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())

