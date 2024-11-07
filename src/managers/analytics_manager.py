import pandas as pd
from typing import Dict, List, Tuple
from ..database.database import PromptDatabase

class AnalyticsManager:
    """프롬프트 분석을 담당하는 클래스"""
    
    def __init__(self, database: PromptDatabase):
        self.database = database

    def get_creation_trends(self) -> Tuple[List, List]:
        """프롬프트 생성 추이 분석"""
        history = self.database.get_history()
        
        if history.empty:
            return [], []
            
        try:
            history['created_at'] = pd.to_datetime(history['created_at'])
            daily_counts = (
                history.groupby(history['created_at'].dt.date)
                .size()
                .reset_index()
            )
            return daily_counts['created_at'].tolist(), daily_counts[0].tolist()
        except Exception as e:
            print(f"Error in get_creation_trends: {str(e)}")
            return [], []

    def get_model_usage_stats(self) -> Dict[str, int]:
        """모델별 사용 통계"""
        history = self.database.get_history()
        
        if history.empty:
            return {}
            
        try:
            if 'model' in history.columns:
                return history['model'].value_counts().to_dict()
            return {}
        except Exception as e:
            print(f"Error in get_model_usage_stats: {str(e)}")
            return {}

    def get_category_stats(self) -> Dict[str, int]:
        """카테고리별 통계"""
        history = self.database.get_history()
        
        if history.empty:
            return {}
            
        try:
            if 'category' in history.columns:
                return history['category'].value_counts().to_dict()
            return {}
        except Exception as e:
            print(f"Error in get_category_stats: {str(e)}")
            return {}

    def get_user_contribution_stats(self) -> Dict[str, Dict[str, int]]:
        """사용자별 기여도 통계"""
        history = self.database.get_history()
        
        if history.empty:
            return {
                'prompt_count': {},
                'best_prompts': {}
            }
        
        stats = {
            'prompt_count': {},
            'best_prompts': {}
        }
        
        try:
            if 'created_by' in history.columns:
                stats['prompt_count'] = history['created_by'].value_counts().to_dict()
                
                if 'is_best' in history.columns:
                    best_prompts = history[history['is_best'] == True]
                    if not best_prompts.empty:
                        stats['best_prompts'] = best_prompts['created_by'].value_counts().to_dict()
                        
        except Exception as e:
            print(f"Error in get_user_contribution_stats: {str(e)}")
            
        return stats