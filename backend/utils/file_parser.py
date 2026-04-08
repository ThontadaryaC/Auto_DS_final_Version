import pandas as pd
from fastapi import UploadFile
import io
import os

async def parse_file(file_input: UploadFile | str | bytes, filename: str = None) -> pd.DataFrame | None:
    """Reads an uploaded file (CSV, XLSX, XML), a local file path, or raw bytes and returns a pandas DataFrame."""
    try:
        if isinstance(file_input, UploadFile):
            content = await file_input.read()
            filename = file_input.filename
        elif isinstance(file_input, bytes):
            content = file_input
            # filename should be provided as the second argument
        elif isinstance(file_input, str):
            with open(file_input, "rb") as f:
                content = f.read()
            if not filename:
                filename = os.path.basename(file_input)
        else:
            return None
            
        if not filename:
            return None
            
        file_ext = filename.split('.')[-1].lower()
        
        if file_ext == 'csv':
            return pd.read_csv(io.BytesIO(content))
        elif file_ext in ['xlsx', 'xls']:
            return pd.read_excel(io.BytesIO(content))
        elif file_ext == 'xml':
            try:
                # Explicitly try lxml first for better compatibility
                return pd.read_xml(io.BytesIO(content), parser='lxml')
            except Exception as e:
                print(f"LXML parsing failed, falling back to etree: {e}")
                return pd.read_xml(io.BytesIO(content), parser='etree')
        else:
            return None
    except Exception as e:
        import traceback
        print(f"Error parsing file: {e}")
        traceback.print_exc()
        return None
