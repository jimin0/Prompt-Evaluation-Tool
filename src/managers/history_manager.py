from typing import Dict, List, Optional
from datetime import datetime
from ..database.database import PromptDatabase

class HistoryManager:
    """프롬프트 히스토리 관리를 담당하는 클래스"""
    
    def __init__(self, database: PromptDatabase):
        self.database = database

    def get_history(self, filters: Optional[Dict] = None) -> List[Dict]:
        """필터링된 히스토리 조회"""
        history = self.database.get_history()
        
        if filters:
            if filters.get('model'):
                history = history[history['model'].isin(filters['model'])]
            if filters.get('version'):
                history = history[history['version'].isin(filters['version'])]
            if filters.get('category'):
                history = history[history['category'].isin(filters['category'])]
            if filters.get('date_range'):
                start_date, end_date = filters['date_range']
                history = history[
                    (history['created_at'].dt.date >= start_date) &
                    (history['created_at'].dt.date <= end_date)
                ]
        
        return history

    def get_change_logs(self, prompt_id: Optional[int] = None) -> List[Dict]:
        """변경 이력 조회"""
        return self.database.get_change_logs(prompt_id)

    def export_history(self, data: List[Dict], format: str = 'csv') -> bytes:
        """히스토리 내보내기"""
        if format == 'csv':
            import pandas as pd
            df = pd.DataFrame(data)
            return df.to_csv(index=False).encode('utf-8')
        raise ValueError(f"Unsupported format: {format}")