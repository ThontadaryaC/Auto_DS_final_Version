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
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def update_upload_ai_data(upload_id, semantic_profile, observation):
    conn = tidb_manager.get_connection()
    if not conn:
        return False
    
    try:
        import json
        cursor = conn.cursor()
        profile_json = json.dumps(semantic_profile)
        query = "UPDATE uploads SET semantic_profile = %s, observation = %s WHERE id = %s"
        cursor.execute(query, (profile_json, observation, upload_id))
        conn.commit()
        return True
    except Error as e:
        print(f"Error updating AI data in TiDB: {e}")
        return False
    finally:
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
        # Clear child records first
        cursor.execute("DELETE FROM dataset_records")
        # Then clear main registry
        cursor.execute("DELETE FROM uploads")
        conn.commit()
        print("TiDB Registry and associated dataset records cleared.")
    except Error as e:
        print(f"Error clearing history in TiDB: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


# Initialize on import
init_db()
