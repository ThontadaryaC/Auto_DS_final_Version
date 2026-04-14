from core.tidb import tidb_manager
from datetime import datetime
from mysql.connector import Error

def init_db():
    # Initialize TiDB tables
    tidb_manager.init_db()

def log_upload(filename, file_path, record_count):
    conn = tidb_manager.get_connection()
    if not conn:
        print("Failed to log upload: TiDB connection unavailable.")
        return
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO uploads (filename, file_path, upload_date, record_count) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (filename, file_path, datetime.now(), record_count))
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error logging upload to TiDB: {e}")
        return None
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def get_upload_history():
    conn = tidb_manager.get_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM uploads ORDER BY upload_date DESC")
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"Error fetching history from TiDB: {e}")
        return []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def get_upload_by_id(upload_id):
    conn = tidb_manager.get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM uploads WHERE id = %s", (upload_id,))
        row = cursor.fetchone()
        return row
    except Error as e:
        print(f"Error fetching upload by ID from TiDB: {e}")
        return None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def clear_upload_history():
    conn = tidb_manager.get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM uploads")
        conn.commit()
    except Error as e:
        print(f"Error clearing history in TiDB: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# Initialize on import
init_db()
