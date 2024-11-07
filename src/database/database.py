# src/database/database.py
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Union
from contextlib import contextmanager
from .models import Prompt, ChangeLog

class DatabaseError(Exception):
    """데이터베이스 관련 커스텀 예외"""
    pass

class PromptDatabase:
    """프롬프트 데이터베이스 관리 클래스"""
    
    def __init__(self, db_path: str = 'prompts.db'):
        self.db_path = db_path
        self.create_tables()

    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseError(f"Database error: {str(e)}")
        finally:
            conn.close()

    def create_tables(self):
        """데이터베이스 테이블 생성"""
        with self.get_connection() as conn:
            # 프롬프트 테이블
            conn.execute('''
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                model TEXT NOT NULL,
                version TEXT NOT NULL,
                category TEXT NOT NULL,
                tags TEXT,
                query TEXT,
                prompt_content TEXT NOT NULL,
                chatbot_response TEXT,
                expected_result TEXT,
                is_best BOOLEAN DEFAULT FALSE,
                changes TEXT,
                improvements TEXT,
                pros TEXT,
                cons TEXT,
                stats TEXT,
                created_by TEXT NOT NULL,
                department TEXT,
                user_role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # 변경 이력 테이블
            conn.execute('''
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

    def save_prompt(self, data: Dict) -> int:
        """프롬프트 저장"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 컬럼과 값 준비
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = list(data.values())
            
            # 프롬프트 저장
            cursor.execute(
                f'INSERT INTO prompts ({columns}) VALUES ({placeholders})',
                values
            )
            
            prompt_id = cursor.lastrowid
            
            # 변경 이력 저장
            log_data = {
                'name': f"Prompt_{data['version']}",
                'title': f"Version {data['version']} Creation",
                'prompt_id': prompt_id,
                'version_number': data['version'],
                'change_summary': data.get('changes', 'Initial creation'),
                'changed_by': data['created_by']
            }
            
            self._save_change_log(conn, log_data)
            
            return prompt_id

    def _save_change_log(self, conn: sqlite3.Connection, data: Dict):
        """변경 이력 저장"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())
        
        conn.execute(
            f'INSERT INTO prompt_change_logs ({columns}) VALUES ({placeholders})',
            values
        )

    def get_prompt(self, prompt_id: int) -> Optional[Dict]:
        """프롬프트 조회"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM prompts WHERE id = ?',
                (prompt_id,)
            )
            result = cursor.fetchone()
            return dict(result) if result else None

    def get_history(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """프롬프트 히스토리 조회"""
        query = 'SELECT * FROM prompts'
        params = []
        
        if filters:
            conditions = []
            if 'model' in filters:
                conditions.append('model IN (' + ','.join(['?']*len(filters['model'])) + ')')
                params.extend(filters['model'])
            if 'category' in filters:
                conditions.append('category IN (' + ','.join(['?']*len(filters['category'])) + ')')
                params.extend(filters['category'])
            if 'date_range' in filters:
                conditions.append('DATE(created_at) BETWEEN ? AND ?')
                params.extend(filters['date_range'])
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC'
        
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_change_logs(self, prompt_id: Optional[int] = None) -> pd.DataFrame:
        """변경 이력 조회"""
        query = '''
        SELECT 
            pcl.*,
            p.title as prompt_title
        FROM prompt_change_logs pcl
        JOIN prompts p ON pcl.prompt_id = p.id
        '''
        
        params = []
        if prompt_id:
            query += ' WHERE pcl.prompt_id = ?'
            params.append(prompt_id)
            
        query += ' ORDER BY pcl.changed_at DESC'
        
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def update_prompt(self, prompt_id: int, data: Dict) -> bool:
        """프롬프트 업데이트"""
        with self.get_connection() as conn:
            # 업데이트할 필드 준비
            update_fields = [f"{key} = ?" for key in data.keys()]
            values = list(data.values())
            values.append(prompt_id)
            
            cursor = conn.execute(
                f'''
                UPDATE prompts 
                SET {', '.join(update_fields)}
                WHERE id = ?
                ''',
                values
            )
            
            success = cursor.rowcount > 0
            
            if success:
                # 변경 이력 기록
                log_data = {
                    'name': f"Prompt_{data['version']}",
                    'title': f"Version {data['version']} Update",
                    'prompt_id': prompt_id,
                    'version_number': data['version'],
                    'change_summary': data.get('changes', 'Updated'),
                    'changed_by': data['created_by']
                }
                self._save_change_log(conn, log_data)
            
            return success

    def search(self, term: str) -> pd.DataFrame:
        """프롬프트 검색"""
        with self.get_connection() as conn:
            search_term = f"%{term}%"
            query = '''
            SELECT * FROM prompts 
            WHERE title LIKE ? 
            OR description LIKE ? 
            OR prompt_content LIKE ? 
            OR query LIKE ? 
            OR chatbot_response LIKE ?
            ORDER BY created_at DESC
            '''
            
            return pd.read_sql_query(
                query, 
                conn, 
                params=(search_term, search_term, search_term, 
                       search_term, search_term)
            )

    def get_prompts(self) -> List[Dict]:
        """모든 프롬프트 기본 정보 조회"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                '''
                SELECT id, title, version, category 
                FROM prompts 
                ORDER BY created_at DESC
                '''
            )
            return [dict(row) for row in cursor.fetchall()]