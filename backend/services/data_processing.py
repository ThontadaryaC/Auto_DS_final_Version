import pandas as pd
import numpy as np

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic data cleaning operations:
    - Drop completely empty rows/cols
    - Drop duplicates
    - Impute missing values (mean for numeric, mode for categorical)
    """
    df = df.dropna(how='all', axis=0)
    df = df.dropna(how='all', axis=1)
    df = df.drop_duplicates()
    
    # Explicit type inference
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass
    
    # Also refine types (Int64, Float64, string, etc.)
    df = df.convert_dtypes()
    
    # Imputation
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].isnull().sum() > 0:
                df[col] = df[col].fillna(df[col].mean())
        else:
            if df[col].isnull().sum() > 0:
                mode_val = df[col].mode()
                if not mode_val.empty:
                    df[col] = df[col].fillna(mode_val[0])
                else:
                    df[col] = df[col].fillna("Unknown")
                    
    return df

def get_insights(df: pd.DataFrame) -> dict:
    """Returns basic DataFrame insights."""
    summary = df.describe(include='all').to_dict()
    info = {
        "rows": len(df),
        "cols": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }
    return info
