from typing import Dict, Optional
from src.database.database import PromptDatabase
from src.utils.text_analyzer import TextAnalyzer

class PromptManager:
    """프롬프트 생성 및 관리를 담당하는 클래스"""
    
    def __init__(self, database: PromptDatabase):
        self.database = database
        self.text_analyzer = TextAnalyzer()

    def create_prompt(self, data: Dict) -> int:
        """새 프롬프트 생성"""
        # 텍스트 분석 추가
        data['stats'] = str(self.text_analyzer.count_stats(data['prompt_content']))
        return self.database.save_prompt(data)

    def update_prompt(self, prompt_id: int, data: Dict) -> bool:
        """프롬프트 업데이트"""
        data['stats'] = str(self.text_analyzer.count_stats(data['prompt_content']))
        return self.database.update_prompt(prompt_id, data)

    def get_prompt(self, prompt_id: int) -> Optional[Dict]:
        """프롬프트 조회"""
        return self.database.get_prompt(prompt_id)

    def validate_version(self, version: str) -> bool:
        """버전 번호 유효성 검사"""
        try:
            major, minor, patch = map(int, version.split('.'))
            return True
        except ValueError:
            return False

    def increment_version(self, version: str) -> str:
        """버전 번호 자동 증가"""
        major, minor, patch = map(int, version.split('.'))
        return f"{major}.{minor}.{patch + 1}"