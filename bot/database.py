import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "memory.db")

def init_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    personality TEXT DEFAULT 'friendly',
                    last_action TEXT,
                    last_response TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_agents (
                    user_id TEXT PRIMARY KEY,
                    personality TEXT DEFAULT 'friendly',
                    memory TEXT,
                    goals TEXT,
                    preferences TEXT,
                    last_active TEXT,
                    custom_name TEXT
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error in init_db: {e}")

def add_message(user_id, role, message):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            timestamp = datetime.utcnow().isoformat()
            cursor.execute('''
                INSERT INTO conversations (user_id, role, message, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, role, message, timestamp))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error in add_message: {e}")

def get_context(user_id, limit=10):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, message FROM conversations
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            ''', (user_id, limit))
            rows = cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in reversed(rows)]
    except sqlite3.Error as e:
        print(f"Database error in get_context: {e}")
        return []

def trim_old_messages(user_id, max_messages=20):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM conversations
                WHERE user_id = ? AND id NOT IN (
                    SELECT id FROM conversations
                    WHERE user_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
            ''', (user_id, user_id, max_messages))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error in trim_old_messages: {e}")

def set_user_personality(user_id, personality):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_profiles (user_id, personality)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET personality=excluded.personality
            ''', (user_id, personality))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error in set_user_personality: {e}")

def get_user_personality(user_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT personality FROM user_profiles WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
        return row[0] if row else 'friendly'
    except sqlite3.Error as e:
        print(f"Database error in get_user_personality: {e}")
        return 'friendly'

def set_last_action(user_id, action, response):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_profiles (user_id, personality, last_action, last_response)
                VALUES (?, COALESCE((SELECT personality FROM user_profiles WHERE user_id = ?), 'friendly'), ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET last_action=?, last_response=?
            ''', (user_id, user_id, action, response, action, response))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error in set_last_action: {e}")

def get_last_action(user_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT last_action, last_response FROM user_profiles WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
        return (row[0], row[1]) if row else (None, None)
    except sqlite3.Error as e:
        print(f"Database error in get_last_action: {e}")
        return (None, None)

def set_user_agent(user_id, personality=None, memory=None, goals=None, preferences=None, last_active=None, custom_name=None):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_agents (user_id, personality, memory, goals, preferences, last_active, custom_name)
                VALUES (?, COALESCE(?, (SELECT personality FROM user_agents WHERE user_id = ?)), COALESCE(?, (SELECT memory FROM user_agents WHERE user_id = ?)), COALESCE(?, (SELECT goals FROM user_agents WHERE user_id = ?)), COALESCE(?, (SELECT preferences FROM user_agents WHERE user_id = ?)), COALESCE(?, (SELECT last_active FROM user_agents WHERE user_id = ?)), COALESCE(?, (SELECT custom_name FROM user_agents WHERE user_id = ?)))
                ON CONFLICT(user_id) DO UPDATE SET
                    personality=COALESCE(excluded.personality, user_agents.personality),
                    memory=COALESCE(excluded.memory, user_agents.memory),
                    goals=COALESCE(excluded.goals, user_agents.goals),
                    preferences=COALESCE(excluded.preferences, user_agents.preferences),
                    last_active=COALESCE(excluded.last_active, user_agents.last_active),
                    custom_name=COALESCE(excluded.custom_name, user_agents.custom_name)
            ''', (
                user_id, personality, user_id, memory, user_id, goals, user_id, preferences, user_id, last_active, user_id, custom_name, user_id
            ))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database error in set_user_agent: {e}")

def get_user_agent(user_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_agents WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
        if row:
            return {
                'user_id': row[0],
                'personality': row[1],
                'memory': row[2],
                'goals': row[3],
                'preferences': row[4],
                'last_active': row[5],
                'custom_name': row[6]
            }
        else:
            return None
    except sqlite3.Error as e:
        print(f"Database error in get_user_agent: {e}")
        return None

def get_user_goal(user_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT goals FROM user_agents WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
        return row[0] if row else None
    except sqlite3.Error as e:
        print(f"Database error in get_user_goal: {e}")
        return None

def get_user_pref(user_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT preferences FROM user_agents WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
        return row[0] if row else None
    except sqlite3.Error as e:
        print(f"Database error in get_user_pref: {e}")
        return None