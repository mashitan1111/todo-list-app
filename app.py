# 工作待办清单桌面应用_精美版.py - 增强版（支持多人协作和完成度管理）
import os
import re
import json
import hashlib
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
from pathlib import Path

# #region agent log
try:
    import requests
    import base64
    # Log successful import
    log_data = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "A",
        "location": "app.py:9",
        "message": "requests import successful",
        "data": {"module": "requests", "status": "ok"},
        "timestamp": int(__import__('time').time() * 1000)
    }
    with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
except ImportError as e:
    # Log import failure
    log_data = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "A",
        "location": "app.py:9",
        "message": "requests import failed",
        "data": {"error": str(e), "status": "failed"},
        "timestamp": int(__import__('time').time() * 1000)
    }
    with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
    raise
# #endregion

# 仅在非 Vercel 环境中导入这些模块
if not os.environ.get('VERCEL'):
    import webbrowser
    import threading

# 导入数据库模块
try:
    from database import (
        init_database, get_all_tasks, create_task, update_task_progress,
        update_task, get_task_updates, delete_task, get_users
    )
    USE_DATABASE = True
except ImportError:
    USE_DATABASE = False
    print("Warning: database module not found, using legacy JSON mode")

app = Flask(__name__)

# 文件路径配置
# 在 Vercel 环境中，使用当前目录；本地开发时使用父目录
if os.environ.get('VERCEL'):
    # Vercel 环境：使用当前文件所在目录
    BASE_DIR = Path(__file__).parent
    # Vercel 环境中这些文件不存在，使用空列表
    TODO_FILE = None
    RECOMMEND_FILE = None
    STATUS_FILE = BASE_DIR / "任务状态.json"  # 使用相对路径
else:
    # 本地开发环境
    BASE_DIR = Path(__file__).parent.parent.parent
    TODO_FILE = BASE_DIR / "工作待办清单.md"
    RECOMMEND_FILE = BASE_DIR / "RAG知识库" / "14_工作内容管理库" / "02_推荐改变清单.md"
    STATUS_FILE = BASE_DIR / "工具和脚本" / "工具脚本" / "任务状态.json"

# 初始化数据库（如果可用）
if USE_DATABASE:
    try:
        init_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        USE_DATABASE = False

def read_markdown_tasks(file_path):
    """读取Markdown文件中的任务（支持多行任务）"""
    if file_path is None or not file_path.exists():
        return []
    
    tasks = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复：使用更强大的正则表达式支持多行任务
    # 匹配 - [ ] 或 - [x] 格式的任务，支持多行内容
    # 使用非贪婪匹配，直到遇到下一个任务标记或文件结尾
    pattern = r'- \[([ x])\] ((?:[^\n]|(?:\n(?!- \[)))+?)(?=\n- \[|$)'
    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        status = match.group(1)
        task_text = match.group(2)
        
        # 清理任务文本：移除多余的空白行，但保留换行符
        task_lines = [line.rstrip() for line in task_text.split('\n')]
        task_text = '\n'.join(task_lines).strip()
        
        # 检测优先级标记
        priority = 'normal'
        if '【紧急】' in task_text or '【P0】' in task_text:
            priority = 'urgent'
        elif '【P1】' in task_text:
            priority = 'high'
        elif '【P2】' in task_text:
            priority = 'normal'
        
        # 检测任务来源
        source = ''
        if '来源：' in task_text:
            source_match = re.search(r'来源：(.+?)(?=\n|$)', task_text)
            if source_match:
                source = source_match.group(1).strip()
        
        # 生成任务ID（使用哈希值，更稳定）
        task_id = hashlib.md5(task_text.encode('utf-8')).hexdigest()
        
        tasks.append({
            'id': task_id,
            'text': task_text,
            'completed': status == 'x',
            'original_status': status,
            'priority': priority,
            'source': source
        })
    
    return tasks

def read_recommendations(file_path):
    """读取推荐改变清单"""
    if file_path is None or not file_path.exists():
        return []
    
    recommendations = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        pattern = r'#### \[(\d{4}-\d{2}-\d{2})\] 推荐改变 #(\d+)'
        matches = re.finditer(pattern, content)
        
        for match in matches:
            date = match.group(1)
            num = match.group(2)
            start = match.end()
            next_match = re.search(r'#### \[', content[start:])
            end = start + next_match.start() if next_match else len(content)
            section = content[start:end]
            
            content_match = re.search(r'##### 改变内容\n(.+?)(?=#####|$)', section, re.DOTALL)
            reason_match = re.search(r'##### 推荐理由\n(.+?)(?=#####|$)', section, re.DOTALL)
            
            if content_match:
                recommendations.append({
                    'date': date,
                    'num': num,
                    'content': content_match.group(1).strip(),
                    'reason': reason_match.group(1).strip() if reason_match else ''
                })
    
    return recommendations

def load_status():
    """加载任务状态"""
    if STATUS_FILE and STATUS_FILE.exists():
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_status(status):
    """保存任务状态"""
    if STATUS_FILE is None:
        return  # Vercel 环境中不保存状态文件
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

def fetch_from_github(github_path):
    """从 GitHub 仓库读取文件内容（Vercel 环境使用）"""
    # #region agent log
    log_data = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "B",
        "location": "app.py:185",
        "message": "fetch_from_github called",
        "data": {"github_path": github_path, "vercel": bool(os.environ.get('VERCEL'))},
        "timestamp": int(__import__('time').time() * 1000)
    }
    try:
        with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
    except: pass
    # #endregion
    
    if not os.environ.get('VERCEL'):
        return None
    
    # GitHub 仓库信息
    repo_owner = "mashitan1111"
    repo_name = "todo-list-app"
    branch = "main"
    
    # 确保路径使用正斜杠
    github_path = github_path.replace("\\", "/")
    
    # 构建 GitHub API URL
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{github_path}"
    
    try:
        response = requests.get(api_url, params={"ref": branch}, timeout=10)
        # #region agent log
        log_data = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": "B",
            "location": "app.py:202",
            "message": "GitHub API response",
            "data": {"status_code": response.status_code, "url": api_url},
            "timestamp": int(__import__('time').time() * 1000)
        }
        try:
            with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        except: pass
        # #endregion
        
        if response.status_code == 200:
            data = response.json()
            if data.get("content"):
                # Base64 解码（GitHub API 返回的 content 是 base64 编码的）
                content = base64.b64decode(data["content"]).decode('utf-8')
                # #region agent log
                log_data = {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "B",
                    "location": "app.py:207",
                    "message": "GitHub content fetched",
                    "data": {"content_length": len(content), "first_100_chars": content[:100]},
                    "timestamp": int(__import__('time').time() * 1000)
                }
                try:
                    with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                except: pass
                # #endregion
                return content
        elif response.status_code == 404:
            print(f"File not found on GitHub: {github_path}")
    except Exception as e:
        print(f"Error fetching from GitHub ({github_path}): {e}")
        # #region agent log
        log_data = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": "B",
            "location": "app.py:212",
            "message": "GitHub fetch error",
            "data": {"error": str(e), "github_path": github_path},
            "timestamp": int(__import__('time').time() * 1000)
        }
        try:
            with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        except: pass
        # #endregion
    
    return None

def sync_tasks_from_github():
    """从 GitHub 同步任务到数据库（仅在 Vercel 环境且数据库为空时）"""
    # #region agent log
    log_data = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "A",
        "location": "app.py:216",
        "message": "sync_tasks_from_github called",
        "data": {"USE_DATABASE": USE_DATABASE, "VERCEL": bool(os.environ.get('VERCEL'))},
        "timestamp": int(__import__('time').time() * 1000)
    }
    try:
        with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
    except: pass
    # #endregion
    
    if not USE_DATABASE or not os.environ.get('VERCEL'):
        return False
    
    try:
        # 检查数据库是否为空
        tasks = get_all_tasks()
        # #region agent log
        log_data = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": "A",
            "location": "app.py:223",
            "message": "Database task count",
            "data": {"task_count": len(tasks) if tasks else 0},
            "timestamp": int(__import__('time').time() * 1000)
        }
        try:
            with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        except: pass
        # #endregion
        
        if tasks:
            return False  # 数据库已有数据，不需要同步
        
        # 从 GitHub 读取 Markdown 文件
        # 尝试多个可能的路径
        github_paths = [
            "圆心工作/工作待办清单.md",
            "工作待办清单.md"
        ]
        
        content = None
        for path in github_paths:
            content = fetch_from_github(path)
            if content:
                break
        
        # #region agent log
        log_data = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": "A",
            "location": "app.py:240",
            "message": "GitHub content check",
            "data": {"content_found": bool(content), "content_length": len(content) if content else 0},
            "timestamp": int(__import__('time').time() * 1000)
        }
        try:
            with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        except: pass
        # #endregion
        
        if not content:
            print("Could not fetch tasks from GitHub")
            return False
        
        # 解析 Markdown 任务
        tasks = []
        pattern = r'- \[([ x])\] ((?:[^\n]|(?:\n(?!- \[)))+?)(?=\n- \[|$)'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        match_count = 0
        
        for match in matches:
            match_count += 1
            status = match.group(1)
            task_text = match.group(2)
            
            # 清理任务文本
            task_lines = [line.rstrip() for line in task_text.split('\n')]
            task_text = '\n'.join(task_lines).strip()
            
            # 检测优先级
            priority = 'normal'
            if '【紧急】' in task_text or '【P0】' in task_text:
                priority = 'urgent'
            elif '【P1】' in task_text:
                priority = 'high'
            
            # 检测来源
            source = ''
            if '来源：' in task_text:
                source_match = re.search(r'来源：(.+?)(?=\n|$)', task_text)
                if source_match:
                    source = source_match.group(1).strip()
            
            # 导入到数据库
            try:
                result = create_task(
                    text=task_text,
                    priority=priority,
                    source=source,
                    creator='GitHub Sync'
                )
                if result.get('success'):
                    # 如果任务已完成，更新状态
                    if status == 'x':
                        update_task_progress(result['task_id'], 100, 'GitHub Sync', 'completed')
                    tasks.append(task_text)
            except Exception as e:
                print(f"Error importing task: {e}")
                # #region agent log
                log_data = {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "C",
                    "location": "app.py:285",
                    "message": "Task import error",
                    "data": {"error": str(e), "task_text_preview": task_text[:50]},
                    "timestamp": int(__import__('time').time() * 1000)
                }
                try:
                    with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                except: pass
                # #endregion
                continue
        
        # #region agent log
        log_data = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": "A",
            "location": "app.py:288",
            "message": "Sync completed",
            "data": {"matches_found": match_count, "tasks_imported": len(tasks)},
            "timestamp": int(__import__('time').time() * 1000)
        }
        try:
            with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        except: pass
        # #endregion
        
        print(f"Synced {len(tasks)} tasks from GitHub")
        return len(tasks) > 0
    except Exception as e:
        print(f"Error syncing from GitHub: {e}")
        return False

@app.route('/')
def index():
    """主页面"""
    # #region agent log
    log_data = {
        "sessionId": "debug-session",
        "runId": "run1",
        "hypothesisId": "A",
        "location": "app.py:294",
        "message": "index() called",
        "data": {"USE_DATABASE": USE_DATABASE, "VERCEL": bool(os.environ.get('VERCEL'))},
        "timestamp": int(__import__('time').time() * 1000)
    }
    try:
        with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
    except: pass
    # #endregion
    
    # 优先使用数据库，否则回退到Markdown+JSON
    if USE_DATABASE:
        try:
            tasks = get_all_tasks()
            # #region agent log
            log_data = {
                "sessionId": "debug-session",
                "runId": "run1",
                "hypothesisId": "A",
                "location": "app.py:300",
                "message": "Initial task load",
                "data": {"task_count": len(tasks) if tasks else 0},
                "timestamp": int(__import__('time').time() * 1000)
            }
            try:
                with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
            except: pass
            # #endregion
            
            # 如果数据库为空且是 Vercel 环境，尝试从 GitHub 同步
            if not tasks and os.environ.get('VERCEL'):
                print("Database is empty, attempting to sync from GitHub...")
                sync_result = sync_tasks_from_github()
                # #region agent log
                log_data = {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A",
                    "location": "app.py:304",
                    "message": "Sync result",
                    "data": {"sync_success": sync_result},
                    "timestamp": int(__import__('time').time() * 1000)
                }
                try:
                    with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                except: pass
                # #endregion
                tasks = get_all_tasks()  # 重新加载
                # #region agent log
                log_data = {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A",
                    "location": "app.py:305",
                    "message": "After sync task load",
                    "data": {"task_count": len(tasks) if tasks else 0},
                    "timestamp": int(__import__('time').time() * 1000)
                }
                try:
                    with open(r"c:\Users\温柔的男子啊\AppData\Roaming\Cursor\logs\20260104T213527\window1\exthost\ms-vscode.powershell\.cursor\debug.log", "a", encoding="utf-8") as f:
                        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
                except: pass
                # #endregion
            
            # 转换数据库格式到前端格式
            for task in tasks:
                task['completed'] = task.get('progress', 0) >= 100 or task.get('status') == 'completed'
        except Exception as e:
            print(f"Error loading from database: {e}, falling back to Markdown")
            tasks = read_markdown_tasks(TODO_FILE) if TODO_FILE else []
            status = load_status()
            for task in tasks:
                task_id = task['id']
                if task_id in status:
                    task['completed'] = status[task_id]
    else:
        tasks = read_markdown_tasks(TODO_FILE) if TODO_FILE else []
        recommendations = read_recommendations(RECOMMEND_FILE) if RECOMMEND_FILE else []
        status = load_status()
        
        # 修复：使用任务ID而不是完整文本作为key
        for task in tasks:
            task_id = task['id']
            # 兼容旧版本：如果使用文本作为key的状态存在，迁移到ID
            task_text = task['text']
            if task_text in status:
                # 迁移旧状态到新ID
                status[task_id] = status[task_text]
                del status[task_text]
                save_status(status)
            
            if task_id in status:
                task['completed'] = status[task_id]
    
    # 读取推荐（如果数据库不可用）
    if not USE_DATABASE:
        recommendations = read_recommendations(RECOMMEND_FILE) if RECOMMEND_FILE else []
    else:
        recommendations = read_recommendations(RECOMMEND_FILE) if RECOMMEND_FILE else []  # 仍然从文件读取推荐
    
    # 按优先级和完成状态分组
    urgent_pending = [t for t in tasks if not t['completed'] and t.get('priority') == 'urgent']
    high_pending = [t for t in tasks if not t['completed'] and t.get('priority') == 'high']
    normal_pending = [t for t in tasks if not t['completed'] and t.get('priority') in ['normal', None]]
    completed_tasks = [t for t in tasks if t['completed']]
    
    total_pending = len(urgent_pending) + len(high_pending) + len(normal_pending)
    completion_rate = len(completed_tasks) / len(tasks) * 100 if tasks else 0
    
    # 获取用户列表（用于筛选）
    users = get_users() if USE_DATABASE else []
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>工作待办清单 - 圆心工作</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', 'Microsoft YaHei', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                background-attachment: fixed;
                min-height: 100vh;
                padding: 20px;
                color: #333;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            
            /* 头部区域 */
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px 40px;
                margin-bottom: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .header-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            
            .header-title {
                font-size: 32px;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .header-date {
                color: #666;
                font-size: 14px;
                font-weight: 400;
            }
            
            /* 统计卡片 */
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.3);
                transition: all 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
            }
            
            .stat-card.urgent {
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
                color: white;
            }
            
            .stat-card.pending {
                background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
                color: white;
            }
            
            .stat-card.completed {
                background: linear-gradient(135deg, #95e1d3 0%, #6bcf7f 100%);
                color: white;
            }
            
            .stat-card.recommend {
                background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
                color: white;
            }
            
            .stat-number {
                font-size: 42px;
                font-weight: 700;
                margin-bottom: 8px;
                line-height: 1;
            }
            
            .stat-label {
                font-size: 14px;
                font-weight: 500;
                opacity: 0.9;
            }
            
            /* 进度条 */
            .progress-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 30px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            }
            
            .progress-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            }
            
            .progress-title {
                font-size: 16px;
                font-weight: 600;
                color: #333;
            }
            
            .progress-percent {
                font-size: 18px;
                font-weight: 700;
                color: #667eea;
            }
            
            .progress-bar {
                width: 100%;
                height: 12px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                position: relative;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                transition: width 0.5s ease;
                box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4);
            }
            
            /* 任务区域 */
            .tasks-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-bottom: 30px;
            }
            
            @media (max-width: 1200px) {
                .tasks-container {
                    grid-template-columns: 1fr;
                }
            }
            
            .task-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .section-header {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #f0f0f0;
            }
            
            .section-icon {
                font-size: 24px;
                margin-right: 12px;
            }
            
            .section-title {
                font-size: 20px;
                font-weight: 600;
                color: #333;
                flex: 1;
            }
            
            .section-count {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            
            /* 任务项 */
            .task-group {
                margin-bottom: 25px;
            }
            
            .group-title {
                font-size: 14px;
                font-weight: 600;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 12px;
                padding: 10px 15px;
                background: rgba(102, 126, 234, 0.1);
                border-radius: 8px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.3s ease;
            }
            
            .group-title:hover {
                background: rgba(102, 126, 234, 0.15);
            }
            
            .group-title.collapsed .collapse-icon {
                transform: rotate(-90deg);
            }
            
            .collapse-icon {
                font-size: 12px;
                transition: transform 0.3s ease;
                color: #667eea;
            }
            
            .task-list {
                overflow: hidden;
                transition: max-height 0.3s ease;
                max-height: 5000px;
            }
            
            .task-list.collapsed {
                max-height: 0;
                overflow: hidden;
            }
            
            .expand-btn {
                text-align: center;
                padding: 12px;
                margin-top: 10px;
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                border-radius: 8px;
                cursor: pointer;
                color: #667eea;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s ease;
                border: 2px dashed rgba(102, 126, 234, 0.3);
            }
            
            .expand-btn:hover {
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
                border-color: rgba(102, 126, 234, 0.5);
                transform: translateY(-2px);
            }
            
            .task-list-hidden {
                display: none;
            }
            
            .task-list-hidden.expanded {
                display: block;
                animation: fadeIn 0.3s ease;
            }
            
            .task-item {
                background: #f8f9fa;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 10px;
                display: flex;
                align-items: flex-start;
                transition: all 0.3s ease;
                border: 2px solid transparent;
                cursor: pointer;
            }
            
            .task-item:hover {
                background: #e9ecef;
                transform: translateX(5px);
                border-color: #667eea;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            }
            
            .task-item.completed {
                opacity: 0.6;
                background: #f0f0f0;
            }
            
            .task-item.urgent {
                border-left: 4px solid #ff6b6b;
            }
            
            .task-item.high {
                border-left: 4px solid #feca57;
            }
            
            .task-item.normal {
                border-left: 4px solid #4ecdc4;
            }
            
            .task-checkbox {
                width: 22px;
                height: 22px;
                margin-right: 12px;
                margin-top: 2px;
                cursor: pointer;
                accent-color: #667eea;
                flex-shrink: 0;
            }
            
            .task-content {
                flex: 1;
            }
            
            .task-text {
                font-size: 15px;
                line-height: 1.6;
                color: #333;
                margin-bottom: 4px;
            }
            
            .task-item.completed .task-text {
                text-decoration: line-through;
                color: #999;
            }
            
            .task-source {
                font-size: 12px;
                color: #999;
                margin-top: 4px;
                font-style: italic;
            }
            
            /* 推荐工作 */
            .recommendations-section {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .recommendation-item {
                background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
                border-left: 4px solid #feca57;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 15px;
                transition: all 0.3s ease;
            }
            
            .recommendation-item:hover {
                transform: translateX(5px);
                box-shadow: 0 4px 12px rgba(254, 202, 87, 0.3);
            }
            
            .recommendation-header {
                display: flex;
                align-items: center;
                margin-bottom: 12px;
            }
            
            .recommendation-badge {
                background: #feca57;
                color: #333;
                padding: 4px 10px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                margin-right: 10px;
            }
            
            .recommendation-date {
                font-size: 12px;
                color: #666;
            }
            
            .recommendation-content {
                font-size: 15px;
                line-height: 1.7;
                color: #333;
                margin-bottom: 8px;
            }
            
            .recommendation-reason {
                font-size: 13px;
                color: #666;
                font-style: italic;
                padding-top: 8px;
                border-top: 1px solid rgba(0, 0, 0, 0.1);
            }
            
            /* 按钮 */
            .btn-refresh {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                margin-bottom: 20px;
            }
            
            .btn-refresh:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            .btn-refresh:active {
                transform: translateY(0);
            }
            
            /* 空状态 */
            .empty-state {
                text-align: center;
                padding: 40px 20px;
                color: #999;
            }
            
            .empty-icon {
                font-size: 48px;
                margin-bottom: 16px;
                opacity: 0.5;
            }
            
            .empty-text {
                font-size: 16px;
            }
            
            /* 动画 */
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .task-item, .recommendation-item {
                animation: fadeIn 0.3s ease;
            }
            
            /* 任务创建模态框 */
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(5px);
            }
            
            .modal-content {
                background-color: white;
                margin: 5% auto;
                padding: 30px;
                border-radius: 20px;
                width: 90%;
                max-width: 600px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                animation: slideDown 0.3s ease;
            }
            
            @keyframes slideDown {
                from {
                    transform: translateY(-50px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #f0f0f0;
            }
            
            .modal-title {
                font-size: 24px;
                font-weight: 600;
                color: #333;
            }
            
            .close {
                font-size: 28px;
                font-weight: bold;
                color: #999;
                cursor: pointer;
                transition: color 0.3s;
            }
            
            .close:hover {
                color: #333;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            .form-label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #333;
                font-size: 14px;
            }
            
            .form-input, .form-select, .form-textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                font-family: inherit;
                transition: border-color 0.3s;
            }
            
            .form-input:focus, .form-select:focus, .form-textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .form-textarea {
                min-height: 100px;
                resize: vertical;
            }
            
            .form-actions {
                display: flex;
                gap: 10px;
                justify-content: flex-end;
                margin-top: 30px;
            }
            
            .btn {
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }
            
            .btn-secondary {
                background: #f0f0f0;
                color: #333;
            }
            
            .btn-secondary:hover {
                background: #e0e0e0;
            }
            
            /* 任务进度显示 */
            .task-progress-container {
                margin-top: 8px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .task-progress-bar {
                flex: 1;
                height: 6px;
                background: #e9ecef;
                border-radius: 3px;
                overflow: hidden;
            }
            
            .task-progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #4ecdc4 0%, #44a08d 100%);
                transition: width 0.3s ease;
            }
            
            .task-progress-text {
                font-size: 12px;
                color: #666;
                font-weight: 600;
                min-width: 40px;
            }
            
            .task-assignee {
                font-size: 12px;
                color: #999;
                margin-top: 4px;
            }
            
            .task-meta {
                display: flex;
                gap: 10px;
                margin-top: 8px;
                flex-wrap: wrap;
            }
            
            .task-meta-item {
                font-size: 12px;
                color: #666;
                padding: 2px 8px;
                background: #f0f0f0;
                border-radius: 4px;
            }
            
            /* 筛选器 */
            .filters {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 20px;
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                align-items: center;
            }
            
            .filter-group {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .filter-label {
                font-size: 14px;
                font-weight: 600;
                color: #666;
            }
            
            .filter-select {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background: white;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- 头部 -->
            <div class="header">
                <div class="header-top">
                    <h1 class="header-title">📋 工作待办清单</h1>
                    <div class="header-date">🕐 {{ update_time }}</div>
                </div>
                
                <!-- 统计卡片 -->
                <div class="stats-grid">
                    <div class="stat-card urgent">
                        <div class="stat-number">{{ urgent_count }}</div>
                        <div class="stat-label">🚨 紧急任务</div>
                    </div>
                    <div class="stat-card pending">
                        <div class="stat-number">{{ total_pending }}</div>
                        <div class="stat-label">📝 待完成</div>
                    </div>
                    <div class="stat-card completed">
                        <div class="stat-number">{{ completed_count }}</div>
                        <div class="stat-label">✅ 已完成</div>
                    </div>
                    <div class="stat-card recommend">
                        <div class="stat-number">{{ recommend_count }}</div>
                        <div class="stat-label">💡 推荐工作</div>
                    </div>
                </div>
                
                <!-- 进度条 -->
                <div class="progress-section">
                    <div class="progress-header">
                        <div class="progress-title">整体完成进度</div>
                        <div class="progress-percent">{{ completion_rate }}%</div>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {{ completion_rate }}%"></div>
                    </div>
                </div>
                
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <button class="btn-refresh" onclick="location.reload()">🔄 刷新数据</button>
                    <button class="btn-refresh" onclick="showCreateTaskModal()" style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);">➕ 添加新任务</button>
                </div>
            </div>
            
            <!-- 筛选器 -->
            {% if users %}
            <div class="filters">
                <div class="filter-group">
                    <label class="filter-label">负责人：</label>
                    <select class="filter-select" id="filter-assignee" onchange="applyFilters()">
                        <option value="">全部</option>
                        {% for user in users %}
                        <option value="{{ user }}">{{ user }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">状态：</label>
                    <select class="filter-select" id="filter-status" onchange="applyFilters()">
                        <option value="">全部</option>
                        <option value="pending">待处理</option>
                        <option value="in_progress">进行中</option>
                        <option value="completed">已完成</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label class="filter-label">优先级：</label>
                    <select class="filter-select" id="filter-priority" onchange="applyFilters()">
                        <option value="">全部</option>
                        <option value="urgent">紧急</option>
                        <option value="high">高</option>
                        <option value="normal">普通</option>
                    </select>
                </div>
            </div>
            {% endif %}
            
            <!-- 任务区域 -->
            <div class="tasks-container">
                <!-- 待完成任务 -->
                <div class="task-section">
                    <div class="section-header">
                        <span class="section-icon">📌</span>
                        <span class="section-title">待完成任务</span>
                        <span class="section-count">{{ total_pending }}</span>
                    </div>
                    
                    {% if urgent_pending %}
                    <div class="task-group">
                        <div class="group-title" onclick="toggleGroup(this)">
                            <span>🚨 紧急任务 ({{ urgent_pending|length }})</span>
                            <span class="collapse-icon">▼</span>
                        </div>
                        <div class="task-list">
                            {% for task in urgent_pending %}
                            <div class="task-item urgent" onclick="toggleTask(this, '{{ task.id }}', event)">
                                <input type="checkbox" class="task-checkbox" 
                                       data-task="{{ task.id }}"
                                       onclick="event.stopPropagation(); toggleTask(this.closest('.task-item'), '{{ task.id }}', event)">
                                <div class="task-content">
                                    <div class="task-text">{{ task.text|replace('\n', '<br>')|safe }}</div>
                                    {% if task.assignee %}
                                    <div class="task-assignee">👤 {{ task.assignee }}</div>
                                    {% endif %}
                                    {% if task.progress is defined %}
                                    <div class="task-progress-container">
                                        <div class="task-progress-bar">
                                            <div class="task-progress-fill" style="width: {{ task.progress }}%"></div>
                                        </div>
                                        <span class="task-progress-text">{{ task.progress }}%</span>
                                    </div>
                                    {% endif %}
                                    {% if task.source %}
                                    <div class="task-source">📍 {{ task.source }}</div>
                                    {% endif %}
                                    {% if task.due_date %}
                                    <div class="task-meta">
                                        <span class="task-meta-item">📅 {{ task.due_date }}</span>
                                    </div>
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if high_pending %}
                    <div class="task-group">
                        <div class="group-title collapsed" onclick="toggleGroup(this)">
                            <span>⚠️ 高优先级 ({{ high_pending|length }})</span>
                            <span class="collapse-icon">▼</span>
                        </div>
                        <div class="task-list collapsed">
                            {% set high_display = high_pending[:10] %}
                            {% set high_hidden = high_pending[10:] %}
                            {% for task in high_display %}
                            <div class="task-item high" onclick="toggleTask(this, '{{ task.id }}', event)">
                                <input type="checkbox" class="task-checkbox" 
                                       data-task="{{ task.id }}"
                                       onclick="event.stopPropagation(); toggleTask(this.closest('.task-item'), '{{ task.id }}', event)">
                                <div class="task-content">
                                    <div class="task-text">{{ task.text|replace('\n', '<br>')|safe }}</div>
                                    {% if task.assignee %}
                                    <div class="task-assignee">👤 {{ task.assignee }}</div>
                                    {% endif %}
                                    {% if task.progress is defined %}
                                    <div class="task-progress-container">
                                        <div class="task-progress-bar">
                                            <div class="task-progress-fill" style="width: {{ task.progress }}%"></div>
                                        </div>
                                        <span class="task-progress-text">{{ task.progress }}%</span>
                                    </div>
                                    {% endif %}
                                    {% if task.source %}
                                    <div class="task-source">📍 {{ task.source }}</div>
                                    {% endif %}
                                    {% if task.due_date %}
                                    <div class="task-meta">
                                        <span class="task-meta-item">📅 {{ task.due_date }}</span>
                                    </div>
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                            {% if high_hidden|length > 0 %}
                            <div class="expand-btn" onclick="showMore('high', event)">
                                查看全部 {{ high_pending|length }} 个任务 ▼
                            </div>
                            <div class="task-list-hidden" id="high-more">
                                {% for task in high_hidden %}
                                <div class="task-item high" onclick="toggleTask(this, '{{ task.id }}', event)">
                                    <input type="checkbox" class="task-checkbox" 
                                           data-task="{{ task.id }}"
                                           onclick="event.stopPropagation(); toggleTask(this.closest('.task-item'), '{{ task.id }}', event)">
                                    <div class="task-content">
                                        <div class="task-text">{{ task.text|replace('\n', '<br>')|safe }}</div>
                                        {% if task.source %}
                                        <div class="task-source">📍 {{ task.source }}</div>
                                        {% endif %}
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if normal_pending %}
                    <div class="task-group">
                        <div class="group-title collapsed" onclick="toggleGroup(this)">
                            <span>📋 普通任务 ({{ normal_pending|length }})</span>
                            <span class="collapse-icon">▼</span>
                        </div>
                        <div class="task-list collapsed">
                            {% set normal_display = normal_pending[:5] %}
                            {% set normal_hidden = normal_pending[5:] %}
                            {% for task in normal_display %}
                            <div class="task-item normal" onclick="toggleTask(this, '{{ task.id }}', event)">
                                <input type="checkbox" class="task-checkbox" 
                                       data-task="{{ task.id }}"
                                       onclick="event.stopPropagation(); toggleTask(this.closest('.task-item'), '{{ task.id }}', event)">
                                <div class="task-content">
                                    <div class="task-text">{{ task.text|replace('\n', '<br>')|safe }}</div>
                                    {% if task.assignee %}
                                    <div class="task-assignee">👤 {{ task.assignee }}</div>
                                    {% endif %}
                                    {% if task.progress is defined %}
                                    <div class="task-progress-container">
                                        <div class="task-progress-bar">
                                            <div class="task-progress-fill" style="width: {{ task.progress }}%"></div>
                                        </div>
                                        <span class="task-progress-text">{{ task.progress }}%</span>
                                    </div>
                                    {% endif %}
                                    {% if task.source %}
                                    <div class="task-source">📍 {{ task.source }}</div>
                                    {% endif %}
                                    {% if task.due_date %}
                                    <div class="task-meta">
                                        <span class="task-meta-item">📅 {{ task.due_date }}</span>
                                    </div>
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                            {% if normal_hidden|length > 0 %}
                            <div class="expand-btn" onclick="showMore('normal', event)">
                                查看全部 {{ normal_pending|length }} 个任务 ▼
                            </div>
                            <div class="task-list-hidden" id="normal-more">
                                {% for task in normal_hidden %}
                                <div class="task-item normal" onclick="toggleTask(this, '{{ task.id }}', event)">
                                    <input type="checkbox" class="task-checkbox" 
                                           data-task="{{ task.id }}"
                                           onclick="event.stopPropagation(); toggleTask(this.closest('.task-item'), '{{ task.id }}', event)">
                                    <div class="task-content">
                                        <div class="task-text">{{ task.text|replace('\n', '<br>')|safe }}</div>
                                        {% if task.source %}
                                        <div class="task-source">📍 {{ task.source }}</div>
                                        {% endif %}
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if not urgent_pending and not high_pending and not normal_pending %}
                    <div class="empty-state">
                        <div class="empty-icon">🎉</div>
                        <div class="empty-text">太棒了！所有任务都已完成！</div>
                    </div>
                    {% endif %}
                </div>
                
                <!-- 已完成任务 -->
                <div class="task-section">
                    <div class="section-header">
                        <span class="section-icon">✅</span>
                        <span class="section-title">已完成任务</span>
                        <span class="section-count">{{ completed_count }}</span>
                    </div>
                    
                    {% if completed_tasks %}
                    {% for task in completed_tasks[:10] %}
                    <div class="task-item completed" onclick="toggleTask(this, '{{ task.id }}', event)">
                        <input type="checkbox" class="task-checkbox" checked
                               data-task="{{ task.id }}"
                               onclick="event.stopPropagation(); toggleTask(this.closest('.task-item'), '{{ task.id }}', event)">
                        <div class="task-content">
                            <div class="task-text">{{ task.text|replace('\n', '<br>')|safe }}</div>
                        </div>
                    </div>
                    {% endfor %}
                    {% if completed_tasks|length > 10 %}
                    <div class="empty-state">
                        <div class="empty-text">还有 {{ completed_tasks|length - 10 }} 个已完成任务...</div>
                    </div>
                    {% endif %}
                    {% else %}
                    <div class="empty-state">
                        <div class="empty-icon">📝</div>
                        <div class="empty-text">还没有完成的任务</div>
                    </div>
                    {% endif %}
                </div>
            </div>
            
            <!-- 推荐工作 -->
            {% if recommendations %}
            <div class="recommendations-section">
                <div class="section-header">
                    <span class="section-icon">💡</span>
                    <span class="section-title">推荐工作</span>
                    <span class="section-count">{{ recommend_count }}</span>
                </div>
                
                {% for rec in recommendations %}
                <div class="recommendation-item">
                    <div class="recommendation-header">
                        <span class="recommendation-badge">推荐 #{{ rec.num }}</span>
                        <span class="recommendation-date">{{ rec.date }}</span>
                    </div>
                    <div class="recommendation-content">{{ rec.content }}</div>
                    {% if rec.reason %}
                    <div class="recommendation-reason">💭 {{ rec.reason }}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        
        <!-- 任务创建模态框 -->
        <div id="createTaskModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 class="modal-title">➕ 创建新任务</h2>
                    <span class="close" onclick="closeCreateTaskModal()">&times;</span>
                </div>
                <form id="createTaskForm" onsubmit="submitCreateTask(event)">
                    <div class="form-group">
                        <label class="form-label">任务内容 *</label>
                        <textarea class="form-textarea" id="task-text" name="text" required placeholder="请输入任务描述..."></textarea>
                    </div>
                    <div class="form-group">
                        <label class="form-label">优先级</label>
                        <select class="form-select" id="task-priority" name="priority">
                            <option value="normal">普通</option>
                            <option value="high">高</option>
                            <option value="urgent">紧急</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">分类</label>
                        <input type="text" class="form-input" id="task-category" name="category" placeholder="例如：待审核的改变清单">
                    </div>
                    <div class="form-group">
                        <label class="form-label">负责人</label>
                        <input type="text" class="form-input" id="task-assignee" name="assignee" placeholder="输入负责人姓名">
                    </div>
                    <div class="form-group">
                        <label class="form-label">截止日期</label>
                        <input type="date" class="form-input" id="task-due-date" name="due_date">
                    </div>
                    <div class="form-group">
                        <label class="form-label">备注</label>
                        <textarea class="form-textarea" id="task-notes" name="notes" placeholder="可选：添加备注信息..."></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeCreateTaskModal()">取消</button>
                        <button type="submit" class="btn btn-primary">创建任务</button>
                    </div>
                </form>
            </div>
        </div>
        
        <script>
            function toggleTask(element, taskId, event) {
                if (event) {
                    event.stopPropagation();
                }
                const checkbox = element.querySelector('.task-checkbox');
                const completed = !checkbox.checked;
                checkbox.checked = completed;
                
                fetch('/api/toggle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task_id: taskId, completed: completed})
                }).then(() => {
                    setTimeout(() => location.reload(), 300);
                }).catch(err => {
                    console.error('Error toggling task:', err);
                    checkbox.checked = !completed;
                });
            }
            
            function toggleGroup(element) {
                const group = element.closest('.task-group');
                const taskList = group.querySelector('.task-list');
                const isCollapsed = element.classList.contains('collapsed');
                
                if (isCollapsed) {
                    element.classList.remove('collapsed');
                    taskList.classList.remove('collapsed');
                    setTimeout(() => {
                        taskList.style.maxHeight = taskList.scrollHeight + 'px';
                    }, 10);
                } else {
                    taskList.style.maxHeight = taskList.scrollHeight + 'px';
                    setTimeout(() => {
                        taskList.style.maxHeight = '0px';
                    }, 10);
                    setTimeout(() => {
                        element.classList.add('collapsed');
                        taskList.classList.add('collapsed');
                    }, 300);
                }
            }
            
            function showMore(type, event) {
                if (event) {
                    event.stopPropagation();
                }
                const hiddenList = document.getElementById(type + '-more');
                const expandBtn = event.target;
                
                if (hiddenList && expandBtn) {
                    hiddenList.classList.add('expanded');
                    expandBtn.style.display = 'none';
                }
            }
            
            // 任务创建模态框
            function showCreateTaskModal() {
                document.getElementById('createTaskModal').style.display = 'block';
            }
            
            function closeCreateTaskModal() {
                document.getElementById('createTaskModal').style.display = 'none';
                document.getElementById('createTaskForm').reset();
            }
            
            // 点击模态框外部关闭
            window.onclick = function(event) {
                const modal = document.getElementById('createTaskModal');
                if (event.target == modal) {
                    closeCreateTaskModal();
                }
            }
            
            // 提交创建任务
            function submitCreateTask(event) {
                event.preventDefault();
                
                const formData = {
                    text: document.getElementById('task-text').value,
                    priority: document.getElementById('task-priority').value,
                    category: document.getElementById('task-category').value,
                    assignee: document.getElementById('task-assignee').value,
                    due_date: document.getElementById('task-due-date').value,
                    notes: document.getElementById('task-notes').value,
                    creator: 'User'  // 可以从localStorage或cookie获取
                };
                
                fetch('/api/task/create', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        closeCreateTaskModal();
                        setTimeout(() => location.reload(), 300);
                    } else {
                        alert('创建任务失败: ' + (data.error || '未知错误'));
                    }
                })
                .catch(err => {
                    console.error('Error:', err);
                    alert('创建任务时发生错误');
                });
            }
            
            // 更新任务进度
            function updateTaskProgress(taskId, progress) {
                fetch('/api/task/' + taskId + '/progress', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        progress: progress,
                        user: 'User',
                        note: 'Progress updated'
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        setTimeout(() => location.reload(), 300);
                    } else {
                        alert('更新进度失败: ' + (data.error || '未知错误'));
                    }
                })
                .catch(err => {
                    console.error('Error:', err);
                    alert('更新进度时发生错误');
                });
            }
            
            // 筛选功能
            function applyFilters() {
                const assignee = document.getElementById('filter-assignee')?.value || '';
                const status = document.getElementById('filter-status')?.value || '';
                const priority = document.getElementById('filter-priority')?.value || '';
                
                // 简单的客户端筛选（如果需要服务器端筛选，可以调用API）
                const taskItems = document.querySelectorAll('.task-item');
                taskItems.forEach(item => {
                    let show = true;
                    
                    if (assignee) {
                        const assigneeText = item.querySelector('.task-assignee')?.textContent || '';
                        if (!assigneeText.includes(assignee)) {
                            show = false;
                        }
                    }
                    
                    if (status) {
                        const isCompleted = item.classList.contains('completed');
                        if (status === 'completed' && !isCompleted) show = false;
                        if (status === 'pending' && isCompleted) show = false;
                        if (status === 'in_progress' && (isCompleted || !item.querySelector('.task-progress-container'))) show = false;
                    }
                    
                    if (priority) {
                        const priorityClass = item.classList.contains(priority) || 
                                            (priority === 'urgent' && item.classList.contains('urgent')) ||
                                            (priority === 'high' && item.classList.contains('high')) ||
                                            (priority === 'normal' && item.classList.contains('normal'));
                        if (!priorityClass) show = false;
                    }
                    
                    item.style.display = show ? 'flex' : 'none';
                });
            }
            
            // 初始化：展开紧急任务组
            document.addEventListener('DOMContentLoaded', function() {
                const allGroups = document.querySelectorAll('.task-group');
                allGroups.forEach(function(group) {
                    const title = group.querySelector('.group-title');
                    const list = group.querySelector('.task-list');
                    if (title && list) {
                        // 如果标题包含"紧急"，默认展开
                        if (title.textContent.includes('紧急')) {
                            title.classList.remove('collapsed');
                            list.classList.remove('collapsed');
                            list.style.maxHeight = list.scrollHeight + 'px';
                        }
                    }
                });
            });
        </script>
    </body>
    </html>
    """
    
    return render_template_string(html,
        update_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        urgent_pending=urgent_pending,
        high_pending=high_pending,
        normal_pending=normal_pending,
        completed_tasks=completed_tasks,
        urgent_count=len(urgent_pending),
        total_pending=total_pending,
        completed_count=len(completed_tasks),
        recommendations=recommendations,
        recommend_count=len(recommendations),
        completion_rate=round(completion_rate, 1),
        users=users
    )

@app.route('/api/toggle', methods=['POST'])
def toggle_task():
    """切换任务状态（兼容旧版本）"""
    data = request.json
    task_id = data.get('task_id') or data.get('task')
    completed = data.get('completed', False)
    
    if not task_id:
        return jsonify({'success': False, 'error': 'Missing task_id'}), 400
    
    if USE_DATABASE:
        try:
            progress = 100 if completed else 0
            result = update_task_progress(task_id, progress, user='User', note='Toggled status')
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        # 旧版本：使用JSON文件
        status = load_status()
        
        # 如果传入的是旧格式（任务文本），尝试转换为ID
        if len(task_id) > 32:
            tasks = read_markdown_tasks(TODO_FILE) if TODO_FILE else []
            for task in tasks:
                if task['text'] == task_id:
                    task_id = task['id']
                    break
        
        status[task_id] = completed
        save_status(status)
        return jsonify({'success': True})

@app.route('/api/task/create', methods=['POST'])
def create_task_api():
    """创建新任务"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Database not available'}), 503
    
    data = request.json
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'success': False, 'error': 'Task text is required'}), 400
    
    priority = data.get('priority', 'normal')
    category = data.get('category', '')
    assignee = data.get('assignee', '')
    creator = data.get('creator', 'User')
    source = data.get('source', '')
    due_date = data.get('due_date', '')
    notes = data.get('notes', '')
    
    try:
        result = create_task(
            text=text,
            priority=priority,
            category=category,
            assignee=assignee,
            creator=creator,
            source=source,
            due_date=due_date if due_date else None,
            notes=notes
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/task/<task_id>/progress', methods=['POST'])
def update_progress_api(task_id):
    """更新任务进度"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Database not available'}), 503
    
    data = request.json
    progress = data.get('progress', 0)
    user = data.get('user', 'User')
    note = data.get('note', '')
    
    try:
        progress = max(0, min(100, int(progress)))  # 限制在0-100之间
        result = update_task_progress(task_id, progress, user=user, note=note)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/task/<task_id>/update', methods=['POST'])
def update_task_api(task_id):
    """更新任务信息"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Database not available'}), 503
    
    data = request.json
    try:
        result = update_task(task_id, **data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/task/<task_id>/updates', methods=['GET'])
def get_task_updates_api(task_id):
    """获取任务更新历史"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Database not available'}), 503
    
    try:
        limit = request.args.get('limit', 10, type=int)
        updates = get_task_updates(task_id, limit=limit)
        return jsonify({'success': True, 'updates': updates})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/task/<task_id>', methods=['DELETE'])
def delete_task_api(task_id):
    """删除任务"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Database not available'}), 503
    
    try:
        result = delete_task(task_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users_api():
    """获取用户列表"""
    if not USE_DATABASE:
        return jsonify({'success': False, 'error': 'Database not available'}), 503
    
    try:
        users = get_users()
        return jsonify({'success': True, 'users': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def open_browser():
    """延迟打开浏览器（仅本地开发时使用）"""
    if os.environ.get('VERCEL'):
        return  # Vercel 环境中不执行
    import time
    import webbrowser
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

# Vercel需要导出app对象
# 本地开发时运行服务器
if __name__ == '__main__':
    # 检查是否在Vercel环境
    if not os.environ.get('VERCEL'):
        # 本地开发模式
        import threading
        threading.Thread(target=open_browser, daemon=True).start()
        app.run(debug=False, port=5000, use_reloader=False)
    else:
        # Vercel环境，不需要启动服务器
        pass

