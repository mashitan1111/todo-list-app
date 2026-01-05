#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
执行 Git 推送
"""
import os
import sys
import subprocess

def git_push_with_token(token):
    """使用 Token 执行 Git 推送"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查 Git 仓库
    if not os.path.exists(os.path.join(script_dir, ".git")):
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
    except Exception:
        pass
    
    # 设置远程 URL（包含 Token）
    if token:
        token_url = f"https://{token}@github.com/mashitan1111/todo-list-app.git"
        try:
            subprocess.run(
                ["git", "remote", "set-url", "origin", token_url],
                cwd=script_dir,
                capture_output=True,
                timeout=5
            )
        except Exception:
            pass
    
    # 执行推送
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
        
        if result.returncode == 0:
            print("✓ 推送成功！")
            return True
        else:
            print(f"✗ 推送失败: {result.stderr.strip()[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ 推送超时")
        return False
    except Exception as e:
        print(f"✗ 推送异常: {e}")
        return False

def main():
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("✗ 错误: GITHUB_TOKEN 环境变量未设置")
        return 1
    
    success = git_push_with_token(token)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

