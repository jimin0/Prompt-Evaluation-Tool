from datetime import datetime
from typing import Dict, List, Optional
from src.database.database import PromptDatabase
import pandas as pd

class HistoryManager:
    """프롬프트 히스토리 관리를 담당하는 클래스"""
    
    def __init__(self, database: PromptDatabase):
        self.database = database

    def get_history(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """필터링된 히스토리 조회"""
        history = self.database.get_history()
        
        if history.empty:
            return history

        # created_at 컬럼을 datetime 타입으로 변환
        history['created_at'] = pd.to_datetime(history['created_at'])
        
        if filters:
            if filters.get('model'):
                history = history[history['model'].isin(filters['model'])]
            
            if filters.get('version'):
                history = history[history['version'].isin(filters['version'])]
            
            if filters.get('category'):
                history = history[history['category'].isin(filters['category'])]
            
            if filters.get('date_range') and len(filters['date_range']) == 2:
                start_date, end_date = filters['date_range']
                history = history[
                    (history['created_at'].dt.date >= start_date) &
                    (history['created_at'].dt.date <= end_date)
                ]
            
            if filters.get('created_by'):
                history = history[
                    history['created_by'].str.contains(
                        filters['created_by'], 
                        case=False,
                        na=False
                    )
                ]
        
        return history.sort_values('created_at', ascending=False)

    def get_change_logs(self, prompt_id: Optional[int] = None) -> pd.DataFrame:
        """변경 이력 조회"""
        logs = self.database.get_change_logs(prompt_id)
        
        if not logs.empty:
            logs['changed_at'] = pd.to_datetime(logs['changed_at'])
        
        return logs

    def export_history(self, data: pd.DataFrame, format: str = 'csv') -> bytes:
        """히스토리 내보내기"""
        if format.lower() == 'csv':
            return data.to_csv(index=False).encode('utf-8')
        elif format.lower() == 'excel':
            return data.to_excel(index=False).encode('utf-8')
        elif format.lower() == 'json':
            return data.to_json(orient='records').encode('utf-8')
        else:
            raise ValueError(f"지원하지 않는 형식입니다: {format}")