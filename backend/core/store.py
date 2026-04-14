import pandas as pd
from typing import Optional

class AppStore:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.filename: Optional[str] = None
        self.semantic_profile: Optional[dict] = None
        
    def set_data(self, data: pd.DataFrame, filename: str):
        self.df = data
        self.filename = filename
        
    def set_semantic_profile(self, profile: dict):
        self.semantic_profile = profile
        
    def get_data(self) -> Optional[pd.DataFrame]:
        return self.df
        
    def get_filename(self) -> Optional[str]:
        return self.filename
        
    def get_semantic_profile(self) -> Optional[dict]:
        return self.semantic_profile

store = AppStore()
