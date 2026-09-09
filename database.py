import sqlite3
from pathlib import Path
from datetime import datetime
import json


class ConversationDatabase:
    def __init__(self, database_path=None):
        if database_path is None:
            database_path = Path(__file__).parent / "messages.db"
        self.conn = sqlite3.connect(database_path)
        self.cursor = self.conn.cursor()
        self.init_table()

    def init_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTs messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                time_stamp TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def load_history(self):
        self.cursor.execute("SELECT role, content, time_stamp FROM messages ORDER BY id ASC")
        rows = self.cursor.fetchall()
        return [
            {"role": row[0], "content": f"[{row[2]}] {row[1]}"} for row in rows
        ]

    def add_message(self, role, content):
        self.cursor.execute("INSERT INTO messages (role, content, time_stamp) VALUES (?, ?, ?)", 
                            (role, content, datetime.now().strftime("%Y-%m-%d %H:%M")))
        self.conn.commit()

if __name__ == "__main__":
    db = ConversationDatabase()
    history = db.load_history()
    print(json.dumps(history, indent=2, ensure_ascii=False))