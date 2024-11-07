from typing import Dict, List, Tuple
import pandas as pd
from ..database.database import PromptDatabase

class AnalyticsManager:
    """프롬프트 분석을 담당하는 클래스"""
    
    def __init__(self, database: PromptDatabase):
        self.database = database

    def get_creation_trends(self) -> Tuple[List[str], List[int]]:
        """프롬프트 생성 추이 분석"""
        history = self.database.get_history()
        daily_counts = (
            history.groupby(pd.to_datetime(history['created_at']).dt.date)
            .size()
            .reset_index()
        )
        return daily_counts['created_at'].tolist(), daily_counts[0].tolist()

    def get_model_usage_stats(self) -> Dict[str, int]:
        """모델별 사용 통계"""
        history = self.database.get_history()
        return history['model'].value_counts().to_dict()

    def get_category_stats(self) -> Dict[str, int]:
        """카테고리별 통계"""
        history = self.database.get_history()
        return history['category'].value_counts().to_dict()

    def get_user_contribution_stats(self) -> Dict[str, Dict[str, int]]:
        """사용자별 기여도 통계"""
        history = self.database.get_history()
        stats = {
            'prompt_count': history['created_by'].value_counts().to_dict(),
            'best_prompts': history[history['is_best']]['created_by'].value_counts().to_dict()
        }
        return stats