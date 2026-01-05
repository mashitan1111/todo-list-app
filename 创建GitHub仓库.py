#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动创建 GitHub 仓库（如果不存在）
"""
import os
import sys
import requests
import json
import time

# 日志配置
LOG_PATH = r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log"
SESSION_ID = "debug-session"
RUN_ID = "post-fix"

def write_log(hypothesis_id, location, message, data):
    """写入调试日志"""
    log_entry = {
        "id": f"log_{int(time.time() * 1000)}",
        "timestamp": int(time.time() * 1000),
        "location": location,
        "message": message,
        "data": data,
        "sessionId": SESSION_ID,
        "runId": RUN_ID,
        "hypothesisId": hypothesis_id
    }
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"日志写入失败: {e}")

def check_repo_exists(token, username, repo_name):
    """检查仓库是否存在"""
    write_log("FIX", "create_repo.py:check_repo_exists", "检查仓库是否存在", {
        "username": username,
        "repo_name": repo_name
    })
    
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        write_log("FIX", "create_repo.py:check_repo_exists", "API响应", {
            "status_code": response.status_code,
            "exists": response.status_code == 200
        })
        return response.status_code == 200
    except Exception as e:
        write_log("FIX", "create_repo.py:check_repo_exists", "检查异常", {"error": str(e)})
        return False

def create_repo(token, username, repo_name):
    """创建 GitHub 仓库"""
    write_log("FIX", "create_repo.py:create_repo", "开始创建仓库", {
        "username": username,
        "repo_name": repo_name
    })
    
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
        "auto_init": False  # 不初始化 README，避免冲突
    }
    
    try:
        write_log("FIX", "create_repo.py:create_repo", "发送创建请求", {"data": data})
        response = requests.post(url, headers=headers, json=data, timeout=10)
        write_log("FIX", "create_repo.py:create_repo", "创建响应", {
            "status_code": response.status_code,
            "response_preview": response.text[:300] if response.text else None
        })
        
        if response.status_code == 201:
            repo_info = response.json()
            write_log("FIX", "create_repo.py:create_repo", "仓库创建成功", {
                "html_url": repo_info.get("html_url"),
                "clone_url": repo_info.get("clone_url")
            })
            return True
        else:
            write_log("FIX", "create_repo.py:create_repo", "创建失败", {
                "status_code": response.status_code,
                "error": response.text[:500] if response.text else None
            })
            return False
    except Exception as e:
        write_log("FIX", "create_repo.py:create_repo", "创建异常", {"error": str(e)})
        return False

def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("✗ 错误: GITHUB_TOKEN 环境变量未设置")
        write_log("FIX", "create_repo.py:main", "Token未设置", {})
        return 1
    
    username = "mashitan1111"
    repo_name = "todo-list-app"
    
    write_log("FIX", "create_repo.py:main", "开始执行", {
        "username": username,
        "repo_name": repo_name,
        "token_exists": bool(token)
    })
    
    # 检查仓库是否存在
    if check_repo_exists(token, username, repo_name):
        print(f"✓ 仓库 {username}/{repo_name} 已存在")
        write_log("FIX", "create_repo.py:main", "仓库已存在，无需创建", {})
        return 0
    
    # 创建仓库
    print(f"正在创建仓库 {username}/{repo_name}...")
    if create_repo(token, username, repo_name):
        print(f"✓ 仓库创建成功: https://github.com/{username}/{repo_name}")
        write_log("FIX", "create_repo.py:main", "仓库创建成功", {})
        return 0
    else:
        print(f"✗ 仓库创建失败")
        write_log("FIX", "create_repo.py:main", "仓库创建失败", {})
        return 1

if __name__ == "__main__":
    sys.exit(main())

