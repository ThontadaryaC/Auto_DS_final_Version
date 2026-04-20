from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
import os
import shutil
from utils.file_parser import parse_file
from core.store import store
from core.database import log_upload
from services.data_processing import clean_dataframe, get_insights
from services.ai_viz import ai_observe_data
from core.mongodb import store_data_in_mongo

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def background_processing(cleaned_df, filename, file_path, upload_id):
    """Handles heavy AI and DB tasks in the background to avoid frontend timeouts."""
    try:
        # 1. AI Semantic Profiling
        from services.semantic_logic import profile_dataset_with_ai
        semantic_profile = profile_dataset_with_ai(cleaned_df, filename)
        store.set_semantic_profile(semantic_profile)
        
        # 2. Store in MongoDB
        store_data_in_mongo(cleaned_df, filename)

        # 3. Store in TiDB HTAP
        from core.tidb import tidb_manager
        tidb_manager.store_dataset_records(cleaned_df, filename, upload_id)
        
        # 4. AI Observation Summary
        observation = ai_observe_data(cleaned_df, filename, semantic_profile)
        store.set_observation(observation)
        store.set_status("completed")
        print(f"Background processing completed for {filename}")
    except Exception as e:
        store.set_status("failed")
        store.set_observation(f"Error in background processing: {e}")
        print(f"Error in background processing for {filename}: {e}")

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls', '.xml')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
        
    # Read content once into memory
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
    # Save file physically
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
        
    # Parse for processing
    df = await parse_file(content, file.filename)
    
    if df is None:
        raise HTTPException(status_code=400, detail="Failed to parse file")
        
    # Clean dataframe automatically
    cleaned_df = clean_dataframe(df)
    
    # Store globally for active session immediately
    store.set_data(cleaned_df, file.filename)
    
    # Log to persistent TiDB database
    upload_id = log_upload(file.filename, file_path, len(cleaned_df))
    
    # NEW: Trigger slow tasks in background
    store.set_status("processing")
    store.set_observation("AI analysis started... Please wait a few seconds.")
    background_tasks.add_task(background_processing, cleaned_df, file.filename, file_path, upload_id)
    
    # Return immediately with basic insights
    # semantic_profile is not yet available, so we pass None
    insights = get_insights(cleaned_df, None)
    
    return {
        "message": f"Successfully uploaded {file.filename}. AI analysis is running in the background.",
        "insights": insights,
        "observation": store.get_observation(),
        "status": store.get_status()
    }

@router.get("/status")
async def get_upload_status():
    return {
        "status": store.get_status(),
        "observation": store.get_observation()
    }
