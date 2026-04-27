import mysql.connector
from mysql.connector import Error, pooling
import os
from dotenv import load_dotenv

load_dotenv()

# Connection Details
TIDB_HOST = os.getenv("TIDB_HOST")
TIDB_PORT = os.getenv("TIDB_PORT", 4000)
TIDB_USER = os.getenv("TIDB_USER")
TIDB_PASSWORD = os.getenv("TIDB_PASSWORD")
TIDB_DB_NAME = os.getenv("TIDB_DB_NAME", "autods")
TIDB_CA_PATH = os.getenv("TIDB_CA_PATH")
TIDB_URL = os.getenv("TIDB_URL")

class TiDBManager:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            try:
                # Use TIDB_URL if provided, else individual params
                config = {}
                if TIDB_URL:
                    if TIDB_URL.startswith("mysql://"):
                        # Basic parsing of mysql://user:password@host:port/dbname?ssl_ca=...
                        import re
                        pattern = r"mysql://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^:]+):(?P<port>\d+)/(?P<dbname>[^?]+)(\?ssl_ca=(?P<ssl_ca>.+))?"
                        match = re.match(pattern, TIDB_URL)
                        if match:
                            config = {
                                "host": match.group("host"),
                                "port": match.group("port"),
                                "user": match.group("user"),
                                "password": match.group("password"),
                                "database": match.group("dbname"),
                                "ssl_ca": match.group("ssl_ca") or TIDB_CA_PATH
                            }
                    elif TIDB_URL.startswith("mysql "):
                        # Parse CLI-style string: mysql -u 'user' -h host -P port -D 'db' -p'pass'
                        import re
                        
                        def get_match(regex, s):
                            m = re.search(regex, s)
                            return m.group(1) or m.group(2) if m else None

                        config = {
                            "user": get_match(r"-u\s+'([^']+)'|-u\s+([^\s]+)", TIDB_URL),
                            "host": get_match(r"-h\s+([^\s]+)", TIDB_URL),
                            "port": get_match(r"-P\s+(\d+)", TIDB_URL),
                            "database": get_match(r"-D\s+'([^']+)'|-D\s+([^\s]+)", TIDB_URL),
                            "password": get_match(r"-p'([^']+)'|-p([^\s]+)", TIDB_URL),
                        }
                        
                        ssl_ca = get_match(r"--ssl-ca=([^\s]+)", TIDB_URL)
                        if ssl_ca and ssl_ca != "<CA_PATH>":
                            config["ssl_ca"] = ssl_ca
                        elif TIDB_CA_PATH:
                            config["ssl_ca"] = TIDB_CA_PATH
                
                if not config or not config.get("host"):
                    config = {
                        "host": TIDB_HOST,
                        "port": TIDB_PORT or 4000,
                        "user": TIDB_USER,
                        "password": TIDB_PASSWORD,
                        "database": TIDB_DB_NAME or "autods",
                        "ssl_ca": TIDB_CA_PATH
                    }

                # Ensure SSL is configured for Cloud
                if config.get("ssl_ca"):
                    config["ssl_verify_cert"] = True

                cls._pool = pooling.MySQLConnectionPool(
                    pool_name="tidb_pool",
                    pool_size=5,
                    **config
                )
                print("TiDB Connection Pool created successfully.")
            except Error as e:
                print(f"Error creating TiDB pool: {e}")
        return cls._pool

    @classmethod
    def get_connection(cls):
        pool = cls.get_pool()
        if pool:
            return pool.get_connection()
        return None

    @classmethod
    def init_db(cls):
        """Initializes the necessary tables in TiDB."""
        conn = cls.get_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            # 1. Metadata Table (replaces SQLite)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploads (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(255) NOT NULL,
                    upload_date DATETIME NOT NULL,
                    record_count INT NOT NULL,
                    semantic_profile JSON,
                    observation TEXT
                ) ENGINE=InnoDB;
            """)
            
            # Migration for existing tables
            try:
                cursor.execute("ALTER TABLE uploads ADD COLUMN semantic_profile JSON")
            except Error:
                pass # Already exists
            try:
                cursor.execute("ALTER TABLE uploads ADD COLUMN observation TEXT")
            except Error:
                pass # Already exists
            
            # 2. Dataset Records Table (Analytical store)
            # We use JSON column for flexibility, or we could flatten it.
            # TiDB handles JSON columns very well for HTAP.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dataset_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    upload_id INT NOT NULL,
                    data JSON NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX (upload_id)
                ) ENGINE=InnoDB;
            """)
            
            conn.commit()
            print("TiDB Tables initialized successfully.")
        except Error as e:
            print(f"Error initializing TiDB: {e}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    @classmethod
    def store_dataset_records(cls, df, filename, upload_id):
        """Stores dataset records in TiDB as JSON for HTAP analysis."""
        if not upload_id:
            print(f"Skipping record storage for {filename}: No valid upload_id provided.")
            return False
            
        conn = cls.get_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            # We store each row as a JSON object in the 'data' column
            import json
            
            # Batch insertion in chunks to handle large datasets
            chunk_size = 1000
            total_records = len(df)
            
            for i in range(0, total_records, chunk_size):
                chunk = df.iloc[i:i+chunk_size]
                records = [ (upload_id, row.to_json()) for _, row in chunk.iterrows() ]
                
                query = "INSERT INTO dataset_records (upload_id, data) VALUES (%s, %s)"
                cursor.executemany(query, records)
                conn.commit() # Commit each chunk
                
            print(f"Successfully stored {total_records} records in TiDB HTAP for upload_id: {upload_id}.")
            return True
        except Error as e:
            print(f"Error storing records in TiDB for {filename}: {e}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()


    @classmethod
    def get_dataset_records(cls, upload_id):
        """Retrieves dataset records from TiDB for a given upload_id."""
        conn = cls.get_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor()
            query = "SELECT data FROM dataset_records WHERE upload_id = %s ORDER BY id ASC"
            cursor.execute(query, (upload_id,))
            rows = cursor.fetchall()
            
            if not rows:
                return None
                
            import json
            import pandas as pd
            # Each row[0] is a JSON string/object
            data_list = []
            for row in rows:
                if isinstance(row[0], str):
                    data_list.append(json.loads(row[0]))
                else:
                    data_list.append(row[0])
            
            return pd.DataFrame(data_list)
        except Error as e:
            print(f"Error retrieving records from TiDB: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

tidb_manager = TiDBManager()
