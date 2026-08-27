import sqlite3
from contextlib import contextmanager

DATABASE_PATH = "classifier.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()

def create_tables():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                text TEXT NOT NULL,
                label TEXT NOT NULL,
                confidence REAL NOT NULL,
                feedback INTEGER DEFAULT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.commit()