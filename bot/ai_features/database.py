import sqlite3
from datetime import datetime

class ConversationDB:
    def __init__(self, db_path="conversations.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)

        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages
                     (user_id INTEGER, timestamp TEXT, role TEXT, content TEXT)''')
        conn.commit()
        conn.close()

    def save_message(self, user_id, role, content):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("INSERT INTO messages (user_id, timestamp, role, content) VALUES (?, ?, ?, ?)",
                  (user_id, datetime.now().isoformat(), role, content))
        conn.commit()
        conn.close()

    def get_user_history(self, user_id, limit=10):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT role, content FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
                  (user_id, limit))
        history = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
        conn.close()
        return history