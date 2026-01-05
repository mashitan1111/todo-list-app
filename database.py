# database.py - 数据库模型和初始化
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

# 数据库文件路径
# 支持Vercel环境变量配置
import os

# Vercel环境使用/tmp目录（临时存储）
if os.environ.get('VERCEL'):
    BASE_DIR = Path('/tmp')
    DB_FILE = BASE_DIR / "tasks.db"
else:
    BASE_DIR = Path(__file__).parent.parent.parent
    DB_FILE = BASE_DIR / "工具和脚本" / "工具脚本" / "tasks.db"

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # 返回字典格式的行
    return conn

def init_database():
    """初始化数据库表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建任务表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            priority TEXT DEFAULT 'normal',
            category TEXT DEFAULT '',
            assignee TEXT DEFAULT '',
            creator TEXT DEFAULT '',
            progress INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            source TEXT DEFAULT '',
            due_date TEXT,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')
    
    # 创建任务更新历史表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            user TEXT NOT NULL,
            progress INTEGER DEFAULT 0,
            status TEXT,
            note TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')
    
    # 创建用户表（可选，用于扩展）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'member',
            created_at TEXT NOT NULL
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_updates_task_id ON task_updates(task_id)')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_FILE}")

def generate_task_id(text):
    """生成任务ID（基于文本内容的MD5哈希）"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def create_task(text, priority='normal', category='', assignee='', creator='', source='', due_date=None, notes=''):
    """创建新任务"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    task_id = generate_task_id(text)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 检查任务是否已存在
    cursor.execute('SELECT id FROM tasks WHERE id = ?', (task_id,))
    if cursor.fetchone():
        conn.close()
        return {'success': False, 'error': 'Task already exists'}
    
    cursor.execute('''
        INSERT INTO tasks (id, text, priority, category, assignee, creator, source, due_date, notes, created_at, updated_at, progress, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'pending')
    ''', (task_id, text, priority, category, assignee, creator, source, due_date, notes, now, now))
    
    # 记录创建历史
    cursor.execute('''
        INSERT INTO task_updates (task_id, user, progress, status, note, updated_at)
        VALUES (?, ?, 0, 'pending', ?, ?)
    ''', (task_id, creator or 'System', 'Task created', now))
    
    conn.commit()
    conn.close()
    return {'success': True, 'task_id': task_id}

def get_all_tasks(filters=None):
    """获取所有任务（支持筛选）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM tasks WHERE 1=1'
    params = []
    
    if filters:
        if filters.get('status'):
            query += ' AND status = ?'
            params.append(filters['status'])
        if filters.get('assignee'):
            query += ' AND assignee = ?'
            params.append(filters['assignee'])
        if filters.get('priority'):
            query += ' AND priority = ?'
            params.append(filters['priority'])
        if filters.get('progress_min') is not None:
            query += ' AND progress >= ?'
            params.append(filters['progress_min'])
        if filters.get('progress_max') is not None:
            query += ' AND progress <= ?'
            params.append(filters['progress_max'])
    
    query += ' ORDER BY priority DESC, created_at DESC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    tasks = []
    for row in rows:
        tasks.append({
            'id': row['id'],
            'text': row['text'],
            'priority': row['priority'],
            'category': row['category'],
            'assignee': row['assignee'],
            'creator': row['creator'],
            'progress': row['progress'],
            'status': row['status'],
            'source': row['source'],
            'due_date': row['due_date'],
            'notes': row['notes'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at'],
            'completed': row['progress'] >= 100 or row['status'] == 'completed'
        })
    
    return tasks

def update_task_progress(task_id, progress, user='System', note=''):
    """更新任务进度"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查任务是否存在
    cursor.execute('SELECT id, status FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    if not task:
        conn.close()
        return {'success': False, 'error': 'Task not found'}
    
    # 更新任务进度和状态
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_status = 'completed' if progress >= 100 else 'in_progress' if progress > 0 else 'pending'
    
    cursor.execute('''
        UPDATE tasks 
        SET progress = ?, status = ?, updated_at = ?
        WHERE id = ?
    ''', (progress, new_status, now, task_id))
    
    # 记录更新历史
    cursor.execute('''
        INSERT INTO task_updates (task_id, user, progress, status, note, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (task_id, user, progress, new_status, note, now))
    
    conn.commit()
    conn.close()
    return {'success': True}

def update_task(task_id, **kwargs):
    """更新任务信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 构建更新字段
    allowed_fields = ['text', 'priority', 'category', 'assignee', 'due_date', 'notes']
    updates = []
    params = []
    
    for field, value in kwargs.items():
        if field in allowed_fields and value is not None:
            updates.append(f'{field} = ?')
            params.append(value)
    
    if not updates:
        conn.close()
        return {'success': False, 'error': 'No valid fields to update'}
    
    updates.append('updated_at = ?')
    params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    params.append(task_id)
    
    query = f'UPDATE tasks SET {", ".join(updates)} WHERE id = ?'
    cursor.execute(query, params)
    
    conn.commit()
    conn.close()
    return {'success': True}

def get_task_updates(task_id, limit=10):
    """获取任务更新历史"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM task_updates 
        WHERE task_id = ? 
        ORDER BY updated_at DESC 
        LIMIT ?
    ''', (task_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    updates = []
    for row in rows:
        updates.append({
            'id': row['id'],
            'user': row['user'],
            'progress': row['progress'],
            'status': row['status'],
            'note': row['note'],
            'updated_at': row['updated_at']
        })
    
    return updates

def delete_task(task_id):
    """删除任务"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 先删除更新历史
    cursor.execute('DELETE FROM task_updates WHERE task_id = ?', (task_id,))
    # 再删除任务
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    
    conn.commit()
    conn.close()
    return {'success': True}

def get_users():
    """获取用户列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT assignee FROM tasks WHERE assignee != "" UNION SELECT DISTINCT creator FROM tasks WHERE creator != ""')
    rows = cursor.fetchall()
    conn.close()
    
    users = [row[0] for row in rows if row[0]]
    return sorted(set(users))

# 初始化数据库（如果不存在）
if __name__ == '__main__':
    init_database()
    print("Database setup complete!")

