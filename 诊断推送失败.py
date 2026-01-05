#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断 GitHub 推送失败问题
"""
import os
import sys
import subprocess
import json
import time
import requests
from pathlib import Path

# 日志配置
LOG_PATH = r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log"
SESSION_ID = "debug-session"
RUN_ID = "run1"

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

def check_hypothesis_a():
    """假设 A: Token 在批处理脚本中无法正确读取"""
    write_log("A", "diagnosis.py:check_hypothesis_a", "开始检查假设A", {})
    
    # 检查环境变量
    token = os.environ.get("GITHUB_TOKEN", "")
    write_log("A", "diagnosis.py:check_hypothesis_a", "读取环境变量", {
        "token_exists": bool(token),
        "token_length": len(token) if token else 0,
        "token_prefix": token[:10] + "..." if token else None
    })
    
    # 检查批处理脚本是否能读取
    try:
        result = subprocess.run(
            ["cmd", "/c", "echo", "%GITHUB_TOKEN%"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=5
        )
        write_log("A", "diagnosis.py:check_hypothesis_a", "CMD读取结果", {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        })
    except Exception as e:
        write_log("A", "diagnosis.py:check_hypothesis_a", "CMD读取异常", {"error": str(e)})
    
    return token

def check_hypothesis_b(token):
    """假设 B: 远程仓库不存在"""
    write_log("B", "diagnosis.py:check_hypothesis_b", "开始检查假设B", {})
    
    if not token:
        write_log("B", "diagnosis.py:check_hypothesis_b", "Token缺失，跳过检查", {})
        return False
    
    headers = {"Authorization": f"token {token}"}
    url = "https://api.github.com/repos/mashitan1111/todo-list-app"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        write_log("B", "diagnosis.py:check_hypothesis_b", "GitHub API响应", {
            "status_code": response.status_code,
            "repo_exists": response.status_code == 200,
            "response_preview": response.text[:200] if response.text else None
        })
        
        if response.status_code == 200:
            repo_info = response.json()
            write_log("B", "diagnosis.py:check_hypothesis_b", "仓库信息", {
                "full_name": repo_info.get("full_name"),
                "private": repo_info.get("private"),
                "html_url": repo_info.get("html_url")
            })
            return True
        else:
            return False
    except Exception as e:
        write_log("B", "diagnosis.py:check_hypothesis_b", "API请求异常", {"error": str(e)})
        return False

def check_hypothesis_c(token):
    """假设 C: Git 推送时 Token 格式不正确"""
    write_log("C", "diagnosis.py:check_hypothesis_c", "开始检查假设C", {})
    
    if not token:
        write_log("C", "diagnosis.py:check_hypothesis_c", "Token缺失，跳过检查", {})
        return
    
    # 检查 Token 格式
    write_log("C", "diagnosis.py:check_hypothesis_c", "Token格式检查", {
        "token_starts_with_ghp": token.startswith("ghp_") if token else False,
        "token_length": len(token) if token else 0,
        "contains_special_chars": any(c in token for c in "@#%&") if token else False
    })
    
    # 测试 URL 格式
    test_url = f"https://{token}@github.com/mashitan1111/todo-list-app.git"
    write_log("C", "diagnosis.py:check_hypothesis_c", "测试URL格式", {
        "url_length": len(test_url),
        "url_contains_token": token in test_url if token else False,
        "url_preview": test_url[:50] + "..." if len(test_url) > 50 else test_url
    })

def check_hypothesis_d():
    """假设 D: Git 配置问题"""
    write_log("D", "diagnosis.py:check_hypothesis_d", "开始检查假设D", {})
    
    try:
        # 检查 Git 用户配置
        result = subprocess.run(
            ["git", "config", "--get", "user.name"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=5,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        user_name = result.stdout.strip() if result.returncode == 0 else None
        
        result = subprocess.run(
            ["git", "config", "--get", "user.email"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=5,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        user_email = result.stdout.strip() if result.returncode == 0 else None
        
        write_log("D", "diagnosis.py:check_hypothesis_d", "Git用户配置", {
            "user_name": user_name,
            "user_email": user_email,
            "user_name_set": bool(user_name),
            "user_email_set": bool(user_email)
        })
        
        # 检查远程仓库配置
        result = subprocess.run(
            ["git", "remote", "-v"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=5,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        write_log("D", "diagnosis.py:check_hypothesis_d", "Git远程配置", {
            "remote_output": result.stdout.strip(),
            "remote_exists": "origin" in result.stdout if result.returncode == 0 else False
        })
        
    except Exception as e:
        write_log("D", "diagnosis.py:check_hypothesis_d", "Git配置检查异常", {"error": str(e)})

def check_hypothesis_e(token):
    """假设 E: 网络连接或 GitHub API 限制问题"""
    write_log("E", "diagnosis.py:check_hypothesis_e", "开始检查假设E", {})
    
    # 检查网络连接
    try:
        response = requests.get("https://github.com", timeout=10)
        write_log("E", "diagnosis.py:check_hypothesis_e", "GitHub连接测试", {
            "status_code": response.status_code,
            "accessible": response.status_code == 200
        })
    except Exception as e:
        write_log("E", "diagnosis.py:check_hypothesis_e", "GitHub连接失败", {"error": str(e)})
    
    # 检查 API 限制（如果 Token 存在）
    if token:
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
            if response.status_code == 200:
                rate_limit = response.json()
                write_log("E", "diagnosis.py:check_hypothesis_e", "API速率限制", {
                    "core_remaining": rate_limit.get("resources", {}).get("core", {}).get("remaining"),
                    "core_limit": rate_limit.get("resources", {}).get("core", {}).get("limit"),
                    "core_reset": rate_limit.get("resources", {}).get("core", {}).get("reset")
                })
        except Exception as e:
            write_log("E", "diagnosis.py:check_hypothesis_e", "API限制检查异常", {"error": str(e)})

def test_git_push(token):
    """测试 Git 推送（实际执行）"""
    write_log("TEST", "diagnosis.py:test_git_push", "开始测试Git推送", {})
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查当前目录是否有 .git
    git_exists = os.path.exists(os.path.join(script_dir, ".git"))
    write_log("TEST", "diagnosis.py:test_git_push", "检查Git仓库", {
        "git_exists": git_exists,
        "script_dir": script_dir
    })
    
    if not git_exists:
        write_log("TEST", "diagnosis.py:test_git_push", "Git仓库不存在，跳过推送测试", {})
        return
    
    # 尝试获取远程 URL
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=5,
            cwd=script_dir
        )
        remote_url = result.stdout.strip() if result.returncode == 0 else None
        write_log("TEST", "diagnosis.py:test_git_push", "当前远程URL", {
            "remote_url": remote_url,
            "contains_token": token in remote_url if (token and remote_url) else False
        })
    except Exception as e:
        write_log("TEST", "diagnosis.py:test_git_push", "获取远程URL异常", {"error": str(e)})
    
    # 尝试推送（dry-run）
    if token:
        try:
            # 设置包含 Token 的 URL
            token_url = f"https://{token}@github.com/mashitan1111/todo-list-app.git"
            result = subprocess.run(
                ["git", "remote", "set-url", "origin", token_url],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=5,
                cwd=script_dir
            )
            write_log("TEST", "diagnosis.py:test_git_push", "设置远程URL", {
                "returncode": result.returncode,
                "stderr": result.stderr.strip()
            })
            
            # 尝试推送（不实际推送，只检查）
            result = subprocess.run(
                ["git", "push", "-u", "origin", "main", "--dry-run"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=10,
                cwd=script_dir
            )
            write_log("TEST", "diagnosis.py:test_git_push", "Git推送测试结果", {
                "returncode": result.returncode,
                "stdout": result.stdout.strip()[:500],
                "stderr": result.stderr.strip()[:500]
            })
        except Exception as e:
            write_log("TEST", "diagnosis.py:test_git_push", "推送测试异常", {"error": str(e)})

def main():
    print("=" * 50)
    print("GitHub 推送失败诊断")
    print("=" * 50)
    print()
    
    # 假设 A: Token 读取问题
    print("[假设 A] 检查 Token 读取...")
    token = check_hypothesis_a()
    print(f"Token 状态: {'✓ 已设置' if token else '✗ 未设置'}")
    print()
    
    # 假设 B: 仓库不存在
    print("[假设 B] 检查远程仓库...")
    repo_exists = check_hypothesis_b(token)
    print(f"仓库状态: {'✓ 存在' if repo_exists else '✗ 不存在'}")
    print()
    
    # 假设 C: Token 格式问题
    print("[假设 C] 检查 Token 格式...")
    check_hypothesis_c(token)
    print("✓ Token 格式检查完成")
    print()
    
    # 假设 D: Git 配置问题
    print("[假设 D] 检查 Git 配置...")
    check_hypothesis_d()
    print("✓ Git 配置检查完成")
    print()
    
    # 假设 E: 网络/API 问题
    print("[假设 E] 检查网络连接...")
    check_hypothesis_e(token)
    print("✓ 网络检查完成")
    print()
    
    # 测试推送
    print("[测试] 执行 Git 推送测试...")
    test_git_push(token)
    print("✓ 推送测试完成")
    print()
    
    print("=" * 50)
    print("诊断完成！")
    print("=" * 50)
    print()
    print(f"日志已保存到: {LOG_PATH}")
    print("请查看日志文件以获取详细信息")

if __name__ == "__main__":
    main()

