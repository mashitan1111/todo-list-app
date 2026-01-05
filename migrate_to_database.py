# migrate_to_database.py - 将现有Markdown和JSON数据迁移到数据库
import json
import re
import hashlib
from pathlib import Path
from database import init_database, create_task, update_task_progress, get_db_connection

BASE_DIR = Path(__file__).parent.parent.parent
TODO_FILE = BASE_DIR / "工作待办清单.md"
STATUS_FILE = BASE_DIR / "工具和脚本" / "工具脚本" / "任务状态.json"

def read_markdown_tasks(file_path):
    """读取Markdown文件中的任务"""
    if not file_path.exists():
        return []
    
    tasks = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'- \[([ x])\] ((?:[^\n]|(?:\n(?!- \[)))+?)(?=\n- \[|$)'
    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        status = match.group(1)
        task_text = match.group(2)
        
        task_lines = [line.rstrip() for line in task_text.split('\n')]
        task_text = '\n'.join(task_lines).strip()
        
        priority = 'normal'
        if '【紧急】' in task_text or '【P0】' in task_text:
            priority = 'urgent'
        elif '【P1】' in task_text:
            priority = 'high'
        elif '【P2】' in task_text:
            priority = 'normal'
        
        source = ''
        if '来源：' in task_text:
            source_match = re.search(r'来源：(.+?)(?=\n|$)', task_text)
            if source_match:
                source = source_match.group(1).strip()
        
        # 检测分类（从Markdown的标题中提取）
        category = ''
        lines_before = content[:match.start()].split('\n')
        for line in reversed(lines_before):
            if line.startswith('##'):
                category = line.replace('##', '').strip()
                break
        
        task_id = hashlib.md5(task_text.encode('utf-8')).hexdigest()
        
        tasks.append({
            'id': task_id,
            'text': task_text,
            'completed': status == 'x',
            'priority': priority,
            'source': source,
            'category': category
        })
    
    return tasks

def load_old_status():
    """加载旧的JSON状态文件"""
    if not STATUS_FILE.exists():
        return {}
    
    with open(STATUS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def migrate():
    """执行迁移"""
    print("Initializing database...")
    init_database()
    
    print("Reading tasks from Markdown...")
    tasks = read_markdown_tasks(TODO_FILE)
    print(f"Found {len(tasks)} tasks in Markdown")
    
    print("Loading old status from JSON...")
    old_status = load_old_status()
    print(f"Found {len(old_status)} status records")
    
    print("\nMigrating tasks to database...")
    migrated = 0
    skipped = 0
    errors = 0
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for task in tasks:
        try:
            # 检查任务是否已存在
            cursor.execute('SELECT id FROM tasks WHERE id = ?', (task['id'],))
            if cursor.fetchone():
                print(f"  Skipping existing task: {task['text'][:50]}...")
                skipped += 1
                continue
            
            # 创建任务
            result = create_task(
                text=task['text'],
                priority=task['priority'],
                category=task['category'],
                source=task['source'],
                creator='System'
            )
            
            if result['success']:
                # 更新进度（如果旧状态中有）
                task_id = task['id']
                if task_id in old_status:
                    completed = old_status[task_id]
                    progress = 100 if completed else 0
                    update_task_progress(task_id, progress, user='System', note='Migrated from old system')
                
                migrated += 1
                print(f"  ✓ Migrated: {task['text'][:50]}...")
            else:
                errors += 1
                print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
        except Exception as e:
            errors += 1
            print(f"  ✗ Exception: {str(e)}")
    
    conn.close()
    
    print(f"\nMigration complete!")
    print(f"  Migrated: {migrated}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors: {errors}")

if __name__ == '__main__':
    migrate()

