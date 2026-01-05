#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动部署到 GitHub 的脚本
使用 GitHub API 创建仓库并提交代码
"""

import os
import subprocess
import json
import requests
from pathlib import Path
import sys
import locale
import time

# Debug logging setup
LOG_PATH = r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log"

def debug_log(session_id, run_id, hypothesis_id, location, message, data=None):
    """Write debug log entry"""
    try:
        log_entry = {
            "sessionId": session_id,
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "timestamp": int(time.time() * 1000),
            "data": data or {}
        }
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

# GitHub 配置
GITHUB_USERNAME = "mashitan1111"
GITHUB_EMAIL = "994404569@qq.com"
# 从环境变量读取 Token，避免硬编码
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
if not GITHUB_TOKEN:
    print("⚠️  警告: 未设置 GITHUB_TOKEN 环境变量")
    print("   请设置环境变量: set GITHUB_TOKEN=your_token_here")
    print("   或在运行脚本前设置: $env:GITHUB_TOKEN='your_token_here'")
REPO_NAME = "todo-list-app"
REPO_DESCRIPTION = "工作待办清单应用 - Flask Web Application"

# 当前目录
CURRENT_DIR = Path(__file__).parent

def create_github_repo():
    """使用 GitHub API 创建仓库"""
    print("正在创建 GitHub 仓库...")
    
    url = f"https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": REPO_NAME,
        "description": REPO_DESCRIPTION,
        "private": False,
        "auto_init": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        repo_info = response.json()
        print(f"✅ 仓库创建成功: {repo_info['html_url']}")
        return repo_info['clone_url']
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            print("⚠️  仓库可能已存在，继续使用现有仓库...")
            return f"https://github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
        else:
            print(f"❌ 创建仓库失败: {e}")
            print(f"响应内容: {e.response.text}")
            return None
    except Exception as e:
        print(f"❌ 创建仓库时出错: {e}")
        return None

def init_git_repo():
    """初始化 Git 仓库"""
    # #region agent log
    debug_log("debug-session", "run1", "A", "deploy_to_github.py:58", "init_git_repo entry", {"current_dir": str(CURRENT_DIR), "default_encoding": locale.getpreferredencoding(), "sys_encoding": sys.getdefaultencoding()})
    # #endregion
    print("\n正在初始化 Git 仓库...")
    
    # 检查是否已经是 Git 仓库
    if (CURRENT_DIR / ".git").exists():
        print("⚠️  已经是 Git 仓库，跳过初始化")
        return True
    
    try:
        # #region agent log
        debug_log("debug-session", "run1", "C", "deploy_to_github.py:69", "Before git init - no encoding specified", {"command": ["git", "init"]})
        # #endregion
        # 初始化 Git
        subprocess.run(["git", "init"], cwd=CURRENT_DIR, check=True, capture_output=True, encoding='utf-8', errors='ignore')
        # #region agent log
        debug_log("debug-session", "run1", "C", "deploy_to_github.py:69", "After git init - with utf-8 encoding", {"success": True})
        # #endregion
        print("✅ Git 仓库初始化成功")
        
        # #region agent log
        debug_log("debug-session", "run1", "C", "deploy_to_github.py:73", "Before git config user.name - no encoding specified", {"username": GITHUB_USERNAME})
        # #endregion
        # 配置用户信息
        subprocess.run(["git", "config", "user.name", GITHUB_USERNAME], 
                      cwd=CURRENT_DIR, check=True, capture_output=True, encoding='utf-8', errors='ignore')
        subprocess.run(["git", "config", "user.email", GITHUB_EMAIL], 
                      cwd=CURRENT_DIR, check=True, capture_output=True, encoding='utf-8', errors='ignore')
        # #region agent log
        debug_log("debug-session", "run1", "C", "deploy_to_github.py:77", "After git config - with utf-8 encoding", {"success": True})
        # #endregion
        print("✅ Git 用户信息配置成功")
        
        return True
    except subprocess.CalledProcessError as e:
        # #region agent log
        debug_log("debug-session", "run1", "A", "deploy_to_github.py:81", "Git init error", {"error": str(e), "error_type": type(e).__name__})
        # #endregion
        print(f"❌ Git 初始化失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ Git 未安装，请先安装 Git")
        print("下载地址: https://git-scm.com/download/win")
        return False
    except UnicodeDecodeError as e:
        # #region agent log
        debug_log("debug-session", "run1", "A", "deploy_to_github.py:87", "UnicodeDecodeError in init_git_repo", {"error": str(e), "encoding": getattr(e, 'encoding', 'unknown'), "position": getattr(e, 'start', 'unknown')})
        # #endregion
        print(f"❌ 编码错误: {e}")
        return False

def add_and_commit_files():
    """添加文件并提交"""
    # #region agent log
    debug_log("debug-session", "run1", "B", "deploy_to_github.py:88", "add_and_commit_files entry")
    # #endregion
    print("\n正在添加文件...")
    
    try:
        # #region agent log
        debug_log("debug-session", "run1", "C", "deploy_to_github.py:94", "Before git add - no encoding specified")
        # #endregion
        # 添加所有文件
        subprocess.run(["git", "add", "."], cwd=CURRENT_DIR, check=True, capture_output=True, encoding='utf-8', errors='ignore')
        # #region agent log
        debug_log("debug-session", "run1", "C", "deploy_to_github.py:94", "After git add - with utf-8 encoding", {"success": True})
        # #endregion
        print("✅ 文件添加成功")
        
        # #region agent log
        debug_log("debug-session", "run1", "B", "deploy_to_github.py:98", "Before git status - text=True without encoding", {"default_encoding": locale.getpreferredencoding()})
        # #endregion
        # 检查是否有更改
        result = subprocess.run(["git", "status", "--porcelain"], 
                              cwd=CURRENT_DIR, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        # #region agent log
        debug_log("debug-session", "run1", "B", "deploy_to_github.py:100", "After git status - with utf-8 encoding", {"stdout_length": len(result.stdout) if result.stdout else 0, "has_changes": bool(result.stdout.strip())})
        # #endregion
        if not result.stdout.strip():
            print("⚠️  没有需要提交的文件")
            return True
        
        # #region agent log
        debug_log("debug-session", "run1", "C", "deploy_to_github.py:105", "Before git commit - no encoding specified")
        # #endregion
        # 提交
        subprocess.run(["git", "commit", "-m", "Initial commit: Todo List App for Vercel"], 
                      cwd=CURRENT_DIR, check=True, capture_output=True, encoding='utf-8', errors='ignore')
        # #region agent log
        debug_log("debug-session", "run1", "C", "deploy_to_github.py:107", "After git commit - with utf-8 encoding", {"success": True})
        # #endregion
        print("✅ 文件提交成功")
        
        return True
    except subprocess.CalledProcessError as e:
        # #region agent log
        debug_log("debug-session", "run1", "A", "deploy_to_github.py:111", "subprocess.CalledProcessError", {"error": str(e), "error_type": type(e).__name__})
        # #endregion
        print(f"❌ 提交文件失败: {e}")
        if hasattr(e, 'stderr') and e.stderr:
            if isinstance(e.stderr, bytes):
                print(f"错误信息: {e.stderr.decode('utf-8', errors='ignore')}")
            else:
                print(f"错误信息: {e.stderr}")
        return False
    except UnicodeDecodeError as e:
        # #region agent log
        debug_log("debug-session", "run1", "A", "deploy_to_github.py:118", "UnicodeDecodeError in add_and_commit_files", {"error": str(e), "encoding": getattr(e, 'encoding', 'unknown'), "position": getattr(e, 'start', 'unknown')})
        # #endregion
        print(f"❌ 编码错误: {e}")
        return False

def push_to_github(clone_url):
    """推送到 GitHub"""
    # #region agent log
    debug_log("debug-session", "run1", "B", "deploy_to_github.py:116", "push_to_github entry", {"default_encoding": locale.getpreferredencoding()})
    # #endregion
    print("\n正在推送到 GitHub...")
    
    try:
        # #region agent log
        debug_log("debug-session", "run1", "B", "deploy_to_github.py:122", "Before git remote -v - text=True without encoding")
        # #endregion
        # 检查是否已有远程仓库
        result = subprocess.run(["git", "remote", "-v"], 
                              cwd=CURRENT_DIR, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        # #region agent log
        debug_log("debug-session", "run1", "B", "deploy_to_github.py:125", "After git remote -v - with utf-8 encoding", {"stdout_length": len(result.stdout) if result.stdout else 0, "has_origin": "origin" in result.stdout if result.stdout else False})
        # #endregion
        
        if "origin" in result.stdout:
            # 更新远程 URL（使用 token）
            remote_url = clone_url.replace("https://", f"https://{GITHUB_TOKEN}@")
            # #region agent log
            debug_log("debug-session", "run1", "C", "deploy_to_github.py:129", "Before git remote set-url - no encoding specified")
            # #endregion
            subprocess.run(["git", "remote", "set-url", "origin", remote_url], 
                          cwd=CURRENT_DIR, check=True, capture_output=True, encoding='utf-8', errors='ignore')
        else:
            # 添加远程仓库（使用 token）
            remote_url = clone_url.replace("https://", f"https://{GITHUB_TOKEN}@")
            # #region agent log
            debug_log("debug-session", "run1", "C", "deploy_to_github.py:134", "Before git remote add - no encoding specified")
            # #endregion
            subprocess.run(["git", "remote", "add", "origin", remote_url], 
                          cwd=CURRENT_DIR, check=True, capture_output=True, encoding='utf-8', errors='ignore')
        
        # #region agent log
        debug_log("debug-session", "run1", "C", "deploy_to_github.py:137", "Before git branch -M - no encoding specified")
        # #endregion
        # 创建并切换到 main 分支
        subprocess.run(["git", "branch", "-M", "main"], 
                      cwd=CURRENT_DIR, check=True, capture_output=True, encoding='utf-8', errors='ignore')
        
        # #region agent log
        debug_log("debug-session", "run1", "B", "deploy_to_github.py:142", "Before git push - text=True without encoding - THIS IS WHERE ERROR OCCURS", {"default_encoding": locale.getpreferredencoding()})
        # #endregion
        # 推送
        print("正在推送代码（这可能需要几秒钟）...")
        result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                              cwd=CURRENT_DIR, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        # #region agent log
        debug_log("debug-session", "run1", "B", "deploy_to_github.py:145", "After git push - with utf-8 encoding", {"returncode": result.returncode, "stdout_length": len(result.stdout) if result.stdout else 0, "stderr_length": len(result.stderr) if result.stderr else 0})
        # #endregion
        
        if result.returncode == 0:
            print("✅ 代码推送成功！")
            print(f"\n🎉 仓库地址: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
            return True
        else:
            print(f"❌ 推送失败: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        # #region agent log
        debug_log("debug-session", "run1", "A", "deploy_to_github.py:153", "subprocess.CalledProcessError in push_to_github", {"error": str(e), "error_type": type(e).__name__})
        # #endregion
        print(f"❌ 推送到 GitHub 失败: {e}")
        if hasattr(e, 'stderr') and e.stderr:
            if isinstance(e.stderr, bytes):
                print(f"错误信息: {e.stderr.decode('utf-8', errors='ignore')}")
            else:
                print(f"错误信息: {e.stderr}")
        return False
    except UnicodeDecodeError as e:
        # #region agent log
        debug_log("debug-session", "run1", "A", "deploy_to_github.py:161", "UnicodeDecodeError in push_to_github", {"error": str(e), "encoding": getattr(e, 'encoding', 'unknown'), "position": getattr(e, 'start', 'unknown'), "object": str(getattr(e, 'object', 'unknown'))[:100] if hasattr(e, 'object') else 'unknown'})
        # #endregion
        print(f"❌ 编码错误: {e}")
        print(f"   编码: {getattr(e, 'encoding', 'unknown')}")
        print(f"   位置: {getattr(e, 'start', 'unknown')}")
        return False
    except Exception as e:
        # #region agent log
        debug_log("debug-session", "run1", "D", "deploy_to_github.py:167", "Unexpected exception in push_to_github", {"error": str(e), "error_type": type(e).__name__})
        # #endregion
        print(f"❌ 推送时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    # #region agent log
    debug_log("debug-session", "run1", "A", "deploy_to_github.py:159", "main entry", {"default_encoding": locale.getpreferredencoding(), "sys_encoding": sys.getdefaultencoding(), "filesystem_encoding": sys.getfilesystemencoding()})
    # #endregion
    print("=" * 60)
    print("  GitHub 自动部署脚本")
    print("=" * 60)
    print(f"\n配置信息:")
    print(f"  用户名: {GITHUB_USERNAME}")
    print(f"  邮箱: {GITHUB_EMAIL}")
    print(f"  仓库名: {REPO_NAME}")
    print(f"  当前目录: {CURRENT_DIR}")
    print("\n" + "=" * 60)
    
    # 步骤1: 创建 GitHub 仓库
    clone_url = create_github_repo()
    if not clone_url:
        print("\n❌ 无法继续，请检查 GitHub Token 和网络连接")
        return
    
    # 步骤2: 初始化 Git
    if not init_git_repo():
        print("\n❌ 无法继续，请先安装 Git")
        return
    
    # 步骤3: 添加并提交文件
    if not add_and_commit_files():
        print("\n❌ 无法继续，请检查文件权限")
        return
    
    # 步骤4: 推送到 GitHub
    if not push_to_github(clone_url):
        print("\n⚠️  推送失败，但你可以手动推送:")
        print(f"   git remote add origin {clone_url}")
        print(f"   git branch -M main")
        print(f"   git push -u origin main")
        return
    
    print("\n" + "=" * 60)
    print("✅ 部署完成！")
    print("=" * 60)
    print(f"\n下一步:")
    print(f"1. 访问仓库: https://github.com/{GITHUB_USERNAME}/{REPO_NAME}")
    print(f"2. 在 Vercel 导入此仓库进行部署")
    print(f"3. 访问 https://vercel.com 并登录")
    print(f"4. 点击 'Add New Project' 并选择此仓库")
    print(f"5. Vercel 会自动检测配置并部署")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

