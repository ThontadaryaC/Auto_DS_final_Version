from fastapi import APIRouter, UploadFile, File, HTTPException
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

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
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
        
    # Parse for processing using the content we already have
    df = await parse_file(content, file.filename)
    
    if df is None:
        raise HTTPException(status_code=400, detail="Failed to parse file")
        
    # Clean dataframe automatically
    cleaned_df = clean_dataframe(df)
    
    # Store globally for single-user session
    store.set_data(cleaned_df, file.filename)
    
    # Log to persistent database
    log_upload(file.filename, file_path, len(cleaned_df))
    
    # Store data in MongoDB Atlas
    store_data_in_mongo(cleaned_df, file.filename)
    
    insights = get_insights(cleaned_df)
    observation = ai_observe_data(cleaned_df)
    
    return {
        "message": f"Successfully uploaded and saved {file.filename}",
        "insights": insights,
        "observation": observation
    }
