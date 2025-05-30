import sqlite3
from datetime import datetime

DB_PATH = "memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            role TEXT,
            message TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_message(user_id, role, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    cursor.execute('''
        INSERT INTO conversations (user_id, role, message, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, role, message, timestamp))
    conn.commit()
    conn.close()

def get_context(user_id, limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT role, message FROM conversations
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
    ''', (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    # Return in order from oldest to newest
    return [{"role": row[0], "content": row[1]} for row in reversed(rows)]

def trim_old_messages(user_id, max_messages=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM conversations
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT -1 OFFSET ?
    ''', (user_id, max_messages))
    rows = cursor.fetchall()
    for row in rows:
        cursor.execute('DELETE FROM conversations WHERE id = ?', (row[0],))
    conn.commit()
    conn.close()

def set_user_personality(user_id, personality):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_profiles (user_id, personality)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET personality=excluded.personality
    ''', (user_id, personality))
    conn.commit()
    conn.close()

def get_user_personality(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT personality FROM user_profiles WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 'friendly'
