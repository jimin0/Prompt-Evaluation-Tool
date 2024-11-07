# prompt_database.py
import pandas as pd
from datetime import datetime
import os

class PromptDatabase:
    def __init__(self, filepath='prompt_history.csv'):
        self.filepath = filepath
        self.history = self._load_history()
        
    def _load_history(self):
        if os.path.exists(self.filepath):
            return pd.read_csv(self.filepath)
        return pd.DataFrame()
        
    def save_prompt(self, data):
        data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history = pd.concat([self.history, pd.DataFrame([data])], ignore_index=True)
        self._save_to_storage()
        
    def get_history(self):
        return self.history
        
    def _save_to_storage(self):
        self.history.to_csv(self.filepath, index=False)
    
    def search(self, term):
        if term:
            mask = self.history['prompt_content'].str.contains(term, case=False, na=False) | \
                   self.history['query'].str.contains(term, case=False, na=False) | \
                   self.history['chatbot_response'].str.contains(term, case=False, na=False)
            return self.history[mask]
        return self.history