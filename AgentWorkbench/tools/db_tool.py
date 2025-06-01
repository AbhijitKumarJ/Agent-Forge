from core import BaseTool
import sqlite3
import os

class SQLiteTool(BaseTool):
    """A tool for interacting with a local SQLite database."""
    def __init__(self, name, description, db_path='agentworkbench.db'):
        super().__init__(name, description)
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        if not os.path.exists(self.db_path):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)')

    def use(self, key, value=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                if value is not None:
                    conn.execute('REPLACE INTO kv (key, value) VALUES (?, ?)', (key, value))
                    print(f"[SQLiteTool] Stored: {key} -> {value}")
                    return True
                else:
                    cur = conn.execute('SELECT value FROM kv WHERE key=?', (key,))
                    row = cur.fetchone()
                    result = row[0] if row else None
                    print(f"[SQLiteTool] Retrieved: {key} -> {result}")
                    return result
        except Exception as e:
            print(f"[SQLiteTool] Error: {e}")
            return None
