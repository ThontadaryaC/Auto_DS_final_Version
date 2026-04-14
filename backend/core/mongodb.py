import os
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "AutoDS_Project"
COLLECTION_NAME = "uploaded_data"

def get_mongo_client():
    if not MONGODB_URI:
        print("MONGODB_URI is not set in environment variables.")
        return None
    try:
        client = MongoClient(MONGODB_URI)
        # Verify connection
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None

def store_data_in_mongo(df, filename):
    """
    Stores the given DataFrame as documents in MongoDB.
    Adds a 'source_file' field and an 'upload_timestamp' to each document.
    """
    client = get_mongo_client()
    if client is None:
        return False

    try:
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Convert DataFrame to list of dictionaries, replacing NaT with None
        # MongoDB cannot serialize NaT (Not a Time) values
        records = df.astype(object).where(pd.notnull(df), None).to_dict('records')
        
        # Add metadata to each record
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for record in records:
            record['source_file'] = filename
            record['upload_timestamp'] = timestamp
            
        # Insert records into MongoDB
        if records:
            result = collection.insert_many(records)
            print(f"Successfully inserted {len(result.inserted_ids)} records from {filename} into MongoDB.")
            return True
        else:
            print("No records to insert.")
            return False
            
    except Exception as e:
        print(f"Error storing data in MongoDB: {e}")
        return False
    finally:
        client.close()
