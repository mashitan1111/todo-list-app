#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查 GitHub 部署环境
"""
import os
import sys
import requests
import json

def check_github_token():
    """检查 GitHub Token"""
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        print("✓ GitHub Token 已设置")
        # 验证 Token 是否有效
        headers = {"Authorization": f"token {token}"}
        try:
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            if response.status_code == 200:
                user_info = response.json()
                print(f"  - Token 有效，用户: {user_info.get('login', 'Unknown')}")
                return True
            else:
                print(f"  ✗ Token 无效 (状态码: {response.status_code})")
                return False
        except Exception as e:
            print(f"  ✗ 验证 Token 时出错: {e}")
            return False
    else:
        print("✗ GitHub Token 未设置")
        print("  请运行以下命令设置 Token:")
        print('  setx GITHUB_TOKEN "YOUR_TOKEN_HERE"')
        print("  然后重新打开命令行窗口")
        return False

def check_network():
    """检查网络连接"""
    try:
        response = requests.get("https://github.com", timeout=10)
        if response.status_code == 200:
            print("✓ 网络连接正常")
            return True
        else:
            print(f"✗ 网络连接异常 (状态码: {response.status_code})")
            return False
    except Exception as e:
        print(f"✗ 网络连接失败: {e}")
        return False

def check_repository(token, username, repo_name):
    """检查远程仓库是否存在"""
    if not token:
        print("✗ 无法检查仓库（Token 未设置）")
        return False
    
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            repo_info = response.json()
            print(f"✓ 仓库存在: {repo_info.get('full_name', repo_name)}")
            print(f"  - 描述: {repo_info.get('description', '无')}")
            print(f"  - 私有: {repo_info.get('private', False)}")
            print(f"  - URL: {repo_info.get('html_url', '')}")
            return True
        elif response.status_code == 404:
            print(f"✗ 仓库不存在: {username}/{repo_name}")
            print(f"  请访问 https://github.com/new 创建仓库")
            return False
        else:
            print(f"✗ 检查仓库时出错 (状态码: {response.status_code})")
            print(f"  响应: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"✗ 检查仓库时出错: {e}")
        return False

def main():
    print("=" * 50)
    print("GitHub 部署环境检查")
    print("=" * 50)
    print()
    
    # 1. 检查 Token
    print("[1/3] 检查 GitHub Token...")
    token = os.environ.get("GITHUB_TOKEN", "")
    token_ok = check_github_token()
    print()
    
    # 2. 检查网络
    print("[2/3] 检查网络连接...")
    network_ok = check_network()
    print()
    
    # 3. 检查仓库
    print("[3/3] 检查远程仓库...")
    username = "mashitan1111"
    repo_name = "todo-list-app"
    repo_ok = check_repository(token, username, repo_name)
    print()
    
    # 总结
    print("=" * 50)
    print("检查结果总结")
    print("=" * 50)
    print(f"GitHub Token: {'✓' if token_ok else '✗'}")
    print(f"网络连接: {'✓' if network_ok else '✗'}")
    print(f"远程仓库: {'✓' if repo_ok else '✗'}")
    print()
    
    if token_ok and network_ok and repo_ok:
        print("✓ 所有检查通过，可以开始部署！")
        return 0
    else:
        print("✗ 部分检查未通过，请先解决上述问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())

