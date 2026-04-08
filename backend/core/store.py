import pandas as pd
from typing import Optional

class AppStore:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.filename: Optional[str] = None
        
    def set_data(self, data: pd.DataFrame, filename: str):
        self.df = data
        self.filename = filename
        
    def get_data(self) -> Optional[pd.DataFrame]:
        return self.df
        
    def get_filename(self) -> Optional[str]:
        return self.filename

store = AppStore()
