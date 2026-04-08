import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        upload_date TEXT NOT NULL,
        record_count INTEGER NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def log_upload(filename, file_path, record_count):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO uploads (filename, file_path, upload_date, record_count)
    VALUES (?, ?, ?, ?)
    ''', (filename, file_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), record_count))
    conn.commit()
    conn.close()

def get_upload_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM uploads ORDER BY upload_date DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_upload_by_id(upload_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM uploads WHERE id = ?', (upload_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def clear_upload_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM uploads')
    conn.commit()
    conn.close()

# Initialize on import
init_db()
