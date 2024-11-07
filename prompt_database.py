# prompt_database.py
import pandas as pd
from datetime import datetime
import os
import sqlite3

class PromptDatabase:
    def __init__(self, db_path='prompts.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
        
    def create_tables(self):
        """데이터베이스 테이블 생성"""
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

    def save_prompt(self, data):
        """프롬프트 저장 및 변경 로그 생성"""
        cursor = self.conn.cursor()
        
        # 프롬프트 데이터 저장
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        
        cursor.execute(
            f'INSERT INTO prompts ({columns}) VALUES ({placeholders})',
            list(data.values())
        )
        
        prompt_id = cursor.lastrowid
        
        # 변경 로그 생성
        log_data = {
            'name': f"Prompt_{data['version']}",
            'title': f"Version {data['version']} Creation" if not data.get('changes') 
                    else f"Version {data['version']} Update",
            'prompt_id': prompt_id,
            'version_number': data['version'],
            'change_summary': data.get('changes', 'Initial creation'),
            'changed_by': data['created_by']
        }
        
        self.save_change_log(log_data)
        
        self.conn.commit()
        return prompt_id

    def get_history(self):
        """프롬프트 히스토리 조회"""
        query = '''
        SELECT * FROM prompts 
        ORDER BY created_at DESC
        '''
        return pd.read_sql_query(query, self.conn)

    def search(self, term):
        """프롬프트 검색"""
        if term:
            query = '''
            SELECT * FROM prompts 
            WHERE prompt_content LIKE ? 
            OR query LIKE ? 
            OR chatbot_response LIKE ?
            OR title LIKE ?
            OR description LIKE ?
            '''
            search_term = f'%{term}%'
            return pd.read_sql_query(
                query, 
                self.conn, 
                params=(search_term, search_term, search_term, search_term, search_term)
            )
        return self.get_history()

    def save_change_log(self, log_data):
        """변경 로그 저장"""
        columns = ', '.join(log_data.keys())
        placeholders = ', '.join(['?' for _ in log_data])
        
        self.conn.execute(
            f'INSERT INTO prompt_change_logs ({columns}) VALUES ({placeholders})',
            list(log_data.values())
        )
        
    def get_change_logs(self, prompt_id=None):
        """변경 로그 조회"""
        query = '''
        SELECT 
            pcl.id,
            pcl.name,
            pcl.title,
            p.title as prompt_title,
            pcl.version_number,
            pcl.change_summary,
            pcl.changed_by,
            pcl.changed_at
        FROM prompt_change_logs pcl
        JOIN prompts p ON pcl.prompt_id = p.id
        '''
        
        if prompt_id:
            query += ' WHERE pcl.prompt_id = ?'
            return pd.read_sql_query(query, self.conn, params=(prompt_id,))
        
        query += ' ORDER BY pcl.changed_at DESC'
        return pd.read_sql_query(query, self.conn)

    def get_prompts(self):
        """모든 프롬프트 기본 정보 조회"""
        query = '''
        SELECT id, title, version, category
        FROM prompts
        ORDER BY created_at DESC
        '''
        return pd.read_sql_query(query, self.conn).to_dict('records')

    def close(self):
        """데이터베이스 연결 종료"""
        self.conn.close()

    def __del__(self):
        """소멸자에서 데이터베이스 연결 종료"""
        try:
            self.conn.close()
        except:
            pass