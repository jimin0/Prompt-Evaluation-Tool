# prompt_database.py
import pandas as pd
from datetime import datetime
import os
import sqlite3

class PromptDatabase:
    def __init__(self, filepath='prompt_history.csv'):
        self.filepath = filepath
        self.history = self._load_history()
        self.conn = sqlite3.connect("prompts.db")

    # Table 생성
    def create_table(self):
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            model TEXT,
            version TEXT,
            category TEXT,
            tags TEXT,
            query TEXT,
            prompt_content TEXT,
            chatbot_response TEXT,
            expected_result TEXT,
            is_best BOOLEAN,
            changes TEXT,
            improvements TEXT,
            pros TEXT,
            cons TEXT,
            stats TEXT,
            created_by TEXT,
            department TEXT,
            user_role TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')      
        
        # 프롬프트 변경 이력 테이블
        self.conn.execute('''
        CREATE TABLE IF NOT EXISTS prompt_change_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            prompt_id INTEGER NOT NULL,
            version_number TEXT NOT NULL,
            change_summary TEXT,
            changed_by TEXT NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prompt_id) REFERENCES prompts (id)
        )
        ''')
        
        self.conn.commit()

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