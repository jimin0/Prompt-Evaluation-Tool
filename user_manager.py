# user_manager.py
import pandas as pd
import os
from datetime import datetime

class UserManager:
    def __init__(self, filepath='users.csv'):
        self.filepath = filepath
        self.users = self._load_users()
        
    def _load_users(self):
        if os.path.exists(self.filepath):
            return pd.read_csv(self.filepath)
        return pd.DataFrame(columns=['user_id', 'username', 'created_at'])
    
    def save_user(self, username):
        if self.user_exists(username):
            return False, "이미 존재하는 사용자입니다."
            
        new_user = {
            'user_id': len(self.users) + 1,
            'username': username,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.users = pd.concat([self.users, pd.DataFrame([new_user])], ignore_index=True)
        self._save_to_storage()
        return True, "사용자가 성공적으로 등록되었습니다."
    
    def user_exists(self, username):
        return username in self.users['username'].values
    
    def get_all_users(self):
        return self.users
    
    def _save_to_storage(self):
        self.users.to_csv(self.filepath, index=False)