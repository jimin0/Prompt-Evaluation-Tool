from typing import List, Dict, Optional
from src.utils.text_analyzer import TextAnalyzer

class TestManager:
    """프롬프트 테스트를 담당하는 클래스"""
    
    def __init__(self):
        self.text_analyzer = TextAnalyzer()

    def run_consistency_test(self, prompt: str, test_cases: List[str]) -> List[Dict]:
        """일관성 테스트 실행"""
        results = []
        for test in test_cases:
            result = {
                'input': test,
                'combined_prompt': f"{prompt}\n\nTest Input: {test}",
                'stats': self.text_analyzer.count_stats(prompt)
            }
            results.append(result)
        return results

    def compare_versions(
        self, 
        old_version: str, 
        new_version: str,
        similarity_threshold: float = 0.8
    ) -> Dict:
        """버전 비교 분석"""
        similar_pairs = self.text_analyzer.find_similar_sentences(
            old_version, 
            new_version, 
            threshold=similarity_threshold
        )
        
        added, removed = self.text_analyzer.get_diff_highlights(old_version, new_version)
        
        return {
            'similar_pairs': similar_pairs,
            'added_lines': added,
            'removed_lines': removed,
            'old_stats': self.text_analyzer.count_stats(old_version),
            'new_stats': self.text_analyzer.count_stats(new_version)
        }

    def validate_prompt_structure(self, prompt: str) -> Dict[str, bool]:
        """프롬프트 구조 유효성 검사"""
        structure = {
            'has_context': len(prompt.strip()) > 0,
            'has_instruction': any(keyword in prompt.lower() 
                                 for keyword in ['please', 'analyze', 'explain', 'describe']),
            'has_example': '예시' in prompt or 'example' in prompt.lower(),
            'has_format_specification': any(char in prompt for char in ['[', ']', '{', '}'])
        }
        return structure