#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能缓存管理器
用途：实现基于文件变更、依赖关系、优先级的智能缓存机制
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

# 工作目录
BASE_DIR = Path(__file__).parent.parent
CACHE_FILE = BASE_DIR / "工作记录系统" / "检查缓存.md"
CACHE_DATA_FILE = BASE_DIR / "工作记录系统" / ".cache_data.json"

# 优先级缓存有效期（天）
PRIORITY_CACHE_EXPIRY = {
    "P0": 1,
    "P1": 3,
    "P2": 7,
    "P3": 14
}


def load_cache_data():
    """加载缓存数据"""
    if CACHE_DATA_FILE.exists():
        with open(CACHE_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_cache_data(data):
    """保存缓存数据"""
    with open(CACHE_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_file_mtime(file_path):
    """获取文件修改时间"""
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if file_path.exists():
        return datetime.fromtimestamp(file_path.stat().st_mtime)
    return None


def check_file_changed(file_path, cached_time):
    """检查文件是否变更"""
    current_mtime = get_file_mtime(file_path)
    if current_mtime is None:
        return True  # 文件不存在，视为变更
    
    if cached_time is None:
        return True  # 没有缓存，需要检查
    
    cached_dt = datetime.fromisoformat(cached_time)
    return current_mtime > cached_dt


def check_cache_valid(cache_entry, priority="P2"):
    """检查缓存是否有效（增强版 - V4.0效率优化）"""
    if not cache_entry:
        return False
    
    # 检查缓存时间
    cache_time_str = cache_entry.get("check_time")
    if not cache_time_str:
        return False
    
    cache_time = datetime.fromisoformat(cache_time_str)
    expiry_days = PRIORITY_CACHE_EXPIRY.get(priority, 7)
    expiry_date = cache_time + timedelta(days=expiry_days)
    
    if datetime.now() > expiry_date:
        return False  # 缓存已过期
    
    # 检查文件是否变更（增强：支持Path对象和字符串）
    file_path = cache_entry.get("file_path")
    if file_path:
        if isinstance(file_path, str):
            file_path = Path(file_path) if not Path(file_path).is_absolute() else Path(file_path)
        elif not isinstance(file_path, Path):
            file_path = Path(str(file_path))
        
        # 如果文件路径是相对路径，转换为绝对路径
        if not file_path.is_absolute():
            file_path = BASE_DIR / file_path
        
        if check_file_changed(file_path, cache_entry.get("file_mtime")):
            return False  # 文件已变更
    
    # 检查依赖文件是否变更（增强：支持多个依赖文件）
    dependencies = cache_entry.get("dependencies", [])
    for dep in dependencies:
        dep_path = dep.get("file_path")
        dep_cached_time = dep.get("cached_time") or dep.get("file_mtime")
        
        if dep_path:
            if isinstance(dep_path, str):
                dep_path = Path(dep_path) if not Path(dep_path).is_absolute() else Path(dep_path)
            elif not isinstance(dep_path, Path):
                dep_path = Path(str(dep_path))
            
            # 如果文件路径是相对路径，转换为绝对路径
            if not dep_path.is_absolute():
                dep_path = BASE_DIR / dep_path
            
            if check_file_changed(dep_path, dep_cached_time):
                return False  # 依赖文件已变更
    
    return True


def update_cache(file_path, check_type, check_result, problems=None, priority="P2", dependencies=None):
    """更新缓存（增强版 - V4.0效率优化）"""
    cache_data = load_cache_data()
    
    # 统一文件路径格式（相对路径）
    if isinstance(file_path, Path):
        if file_path.is_absolute():
            try:
                file_path_str = str(file_path.relative_to(BASE_DIR))
            except ValueError:
                file_path_str = str(file_path)
        else:
            file_path_str = str(file_path)
    else:
        file_path_str = str(file_path)
        file_path = Path(file_path) if not Path(file_path).is_absolute() else Path(file_path)
    
    # 获取文件修改时间
    actual_file_path = BASE_DIR / file_path_str if not Path(file_path_str).is_absolute() else Path(file_path_str)
    file_mtime = get_file_mtime(actual_file_path)
    
    # 处理依赖文件路径
    processed_dependencies = []
    if dependencies:
        for dep in dependencies:
            if isinstance(dep, dict):
                dep_path = dep.get("file_path")
                if dep_path:
                    if isinstance(dep_path, Path):
                        if dep_path.is_absolute():
                            try:
                                dep_path_str = str(dep_path.relative_to(BASE_DIR))
                            except ValueError:
                                dep_path_str = str(dep_path)
                        else:
                            dep_path_str = str(dep_path)
                    else:
                        dep_path_str = str(dep_path)
                    
                    processed_dep = dep.copy()
                    processed_dep["file_path"] = dep_path_str
                    processed_dependencies.append(processed_dep)
                else:
                    processed_dependencies.append(dep)
            else:
                processed_dependencies.append(dep)
    
    cache_entry = {
        "file_path": file_path_str,
        "check_time": datetime.now().isoformat(),
        "check_type": check_type,
        "check_result": check_result,
        "problems": problems or [],
        "priority": priority,
        "file_mtime": file_mtime.isoformat() if file_mtime else None,
        "dependencies": processed_dependencies
    }
    
    cache_data[file_path_str] = cache_entry
    save_cache_data(cache_data)
    
    print(f"✅ 已更新缓存：{file_path_str}")


def get_cache(file_path, priority="P2"):
    """获取缓存"""
    cache_data = load_cache_data()
    file_path_str = str(file_path) if isinstance(file_path, Path) else file_path
    
    cache_entry = cache_data.get(file_path_str)
    
    if cache_entry and check_cache_valid(cache_entry, priority):
        return cache_entry
    
    return None


def should_recheck(file_path, priority="P2"):
    """判断是否需要重新检查"""
    cache_entry = get_cache(file_path, priority)
    return cache_entry is None


def update_cache_markdown():
    """更新检查缓存Markdown文件"""
    cache_data = load_cache_data()
    content = read_cache_markdown()
    
    if content is None:
        return
    
    # 更新检查结果缓存部分
    cache_section = "## 📊 检查结果缓存\n\n"
    
    for file_path, entry in cache_data.items():
        check_time = entry.get("check_time", "")
        check_type = entry.get("check_type", "")
        check_result = entry.get("check_result", "")
        problems = entry.get("problems", [])
        priority = entry.get("priority", "P2")
        
        # 检查缓存是否有效
        is_valid = check_cache_valid(entry, priority)
        status = "✅ 有效" if is_valid else "❌ 已过期"
        
        cache_section += f"### {Path(file_path).name}\n\n"
        cache_section += f"- **文件路径**：`{file_path}`\n"
        cache_section += f"- **检查时间**：{check_time}\n"
        cache_section += f"- **检查类型**：{check_type}\n"
        cache_section += f"- **检查结果**：{check_result}\n"
        cache_section += f"- **优先级**：{priority}\n"
        cache_section += f"- **缓存状态**：{status}\n"
        
        if problems:
            cache_section += f"- **问题列表**：{len(problems)}个问题\n"
        
        cache_section += "\n"
    
    # 替换缓存部分
    pattern = r'(## 📊 检查结果缓存\s*\n)(.*?)(\n---)'
    content = re.sub(pattern, cache_section + r'\3', content, flags=re.DOTALL)
    
    # 更新最后更新时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = re.sub(r'\*\*最后更新\*\*：.*?\n', 
                    f'**最后更新**：{current_time}\n', content)
    
    # 写回文件
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已更新检查缓存Markdown文件")


def read_cache_markdown():
    """读取检查缓存Markdown文件"""
    if not CACHE_FILE.exists():
        return None
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        return f.read()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  检查缓存: python 智能缓存管理器.py check <文件路径> [优先级]")
        print("  更新缓存: python 智能缓存管理器.py update <文件路径> <检查类型> <结果> [优先级]")
        print("  更新Markdown: python 智能缓存管理器.py update-md")
        print("示例:")
        print("  python 智能缓存管理器.py check 'RAG知识库/README.md' P1")
        print("  python 智能缓存管理器.py update 'RAG知识库/README.md' '全面检查' '通过' P1")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "check":
        if len(sys.argv) < 3:
            print("错误：需要文件路径")
            sys.exit(1)
        file_path = sys.argv[2]
        priority = sys.argv[3] if len(sys.argv) > 3 else "P2"
        
        cache = get_cache(file_path, priority)
        if cache:
            print(f"✅ 缓存有效：{file_path}")
            print(f"   检查时间：{cache.get('check_time')}")
            print(f"   检查结果：{cache.get('check_result')}")
        else:
            print(f"❌ 缓存无效或不存在：{file_path}")
            print("   需要重新检查")
    
    elif action == "update":
        if len(sys.argv) < 5:
            print("错误：需要文件路径、检查类型和结果")
            sys.exit(1)
        file_path = sys.argv[2]
        check_type = sys.argv[3]
        check_result = sys.argv[4]
        priority = sys.argv[5] if len(sys.argv) > 5 else "P2"
        
        update_cache(file_path, check_type, check_result, priority=priority)
        update_cache_markdown()
    
    elif action == "update-md":
        update_cache_markdown()
    
    else:
        print(f"错误：未知操作 {action}")
        sys.exit(1)

