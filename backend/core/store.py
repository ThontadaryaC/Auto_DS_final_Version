import pandas as pd
from typing import Optional

class AppStore:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.filename: Optional[str] = None
        self.semantic_profile: Optional[dict] = None
        self.status: str = "idle"
        self.observation: Optional[str] = None
        
    def set_data(self, data: pd.DataFrame, filename: str):
        self.df = data
        self.filename = filename
        
    def set_semantic_profile(self, profile: dict):
        self.semantic_profile = profile

    def set_status(self, status: str):
        self.status = status

    def set_observation(self, observation: str):
        self.observation = observation
        
    def get_data(self) -> Optional[pd.DataFrame]:
        return self.df
        
    def get_filename(self) -> Optional[str]:
        return self.filename
        
    def get_semantic_profile(self) -> Optional[dict]:
        return self.semantic_profile

    def get_status(self) -> str:
        return self.status

    def get_observation(self) -> Optional[str]:
        return self.observation

store = AppStore()
