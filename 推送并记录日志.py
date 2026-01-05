#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
执行 Git 推送并记录详细日志
"""
import os
import sys
import subprocess
import json
import time

# 日志配置
LOG_PATH = r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log"
SESSION_ID = "debug-session"
RUN_ID = "post-fix-push"

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

def git_push_with_token(token):
    """使用 Token 执行 Git 推送"""
    write_log("PUSH", "push_log.py:git_push_with_token", "开始推送", {
        "token_exists": bool(token),
        "token_length": len(token) if token else 0
    })
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查 Git 仓库
    git_exists = os.path.exists(os.path.join(script_dir, ".git"))
    write_log("PUSH", "push_log.py:git_push_with_token", "检查Git仓库", {
        "git_exists": git_exists,
        "script_dir": script_dir
    })
    
    if not git_exists:
        write_log("PUSH", "push_log.py:git_push_with_token", "Git仓库不存在", {})
        return False
    
    # 配置 Git 用户信息
    try:
        subprocess.run(
            ["git", "config", "user.name", "mashitan1111"],
            cwd=script_dir,
            capture_output=True,
            timeout=5
        )
        subprocess.run(
            ["git", "config", "user.email", "994404569@qq.com"],
            cwd=script_dir,
            capture_output=True,
            timeout=5
        )
        write_log("PUSH", "push_log.py:git_push_with_token", "Git用户信息已配置", {})
    except Exception as e:
        write_log("PUSH", "push_log.py:git_push_with_token", "配置Git用户信息异常", {"error": str(e)})
    
    # 设置远程 URL（包含 Token）
    if token:
        token_url = f"https://{token}@github.com/mashitan1111/todo-list-app.git"
        try:
            result = subprocess.run(
                ["git", "remote", "set-url", "origin", token_url],
                cwd=script_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=5
            )
            write_log("PUSH", "push_log.py:git_push_with_token", "设置远程URL", {
                "returncode": result.returncode,
                "stderr": result.stderr.strip()
            })
        except Exception as e:
            write_log("PUSH", "push_log.py:git_push_with_token", "设置远程URL异常", {"error": str(e)})
    
    # 检查远程配置
    try:
        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=script_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=5
        )
        write_log("PUSH", "push_log.py:git_push_with_token", "远程配置", {
            "stdout": result.stdout.strip(),
            "contains_token": token in result.stdout if token else False
        })
    except Exception as e:
        write_log("PUSH", "push_log.py:git_push_with_token", "检查远程配置异常", {"error": str(e)})
    
    # 执行推送
    write_log("PUSH", "push_log.py:git_push_with_token", "开始执行git push", {})
    try:
        result = subprocess.run(
            ["git", "push", "-u", "origin", "main", "--force"],
            cwd=script_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=30
        )
        write_log("PUSH", "push_log.py:git_push_with_token", "推送结果", {
            "returncode": result.returncode,
            "stdout": result.stdout.strip()[:500],
            "stderr": result.stderr.strip()[:500],
            "success": result.returncode == 0
        })
        
        if result.returncode == 0:
            print("✓ 推送成功！")
            return True
        else:
            print(f"✗ 推送失败: {result.stderr.strip()[:200]}")
            return False
    except subprocess.TimeoutExpired:
        write_log("PUSH", "push_log.py:git_push_with_token", "推送超时", {})
        print("✗ 推送超时")
        return False
    except Exception as e:
        write_log("PUSH", "push_log.py:git_push_with_token", "推送异常", {"error": str(e)})
        print(f"✗ 推送异常: {e}")
        return False

def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("✗ 错误: GITHUB_TOKEN 环境变量未设置")
        write_log("PUSH", "push_log.py:main", "Token未设置", {})
        return 1
    
    write_log("PUSH", "push_log.py:main", "开始执行推送", {
        "token_exists": bool(token)
    })
    
    success = git_push_with_token(token)
    
    write_log("PUSH", "push_log.py:main", "推送完成", {
        "success": success
    })
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

