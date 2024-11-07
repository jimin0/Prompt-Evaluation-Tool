from typing import Dict, List, Tuple
import difflib
import re


class TextAnalyzer:
    """텍스트 분석 유틸리티 클래스"""
    
    def count_stats(self, text: str) -> Dict[str, int]:
        """텍스트 통계 분석"""
        if not text:
            return {
                '전체 글자 수': 0,
                '공백 제외 글자 수': 0,
                '단어 수': 0,
                '문장 수': 0,
                '줄 수': 0
            }

        stats = {
            '전체 글자 수': len(text),
            '공백 제외 글자 수': len(text.replace(' ', '')),
            '단어 수': len(text.split()),
            '문장 수': len([s for s in text.split('.') if s.strip()]),
            '줄 수': len(text.splitlines())
        }
        return stats

    def find_similar_sentences(
        self, 
        text1: str, 
        text2: str, 
        threshold: float = 0.8
    ) -> List[Dict]:
        """두 텍스트 간의 유사한 문장 쌍 찾기"""
        sentences1 = [s.strip() for s in text1.split('.') if s.strip()]
        sentences2 = [s.strip() for s in text2.split('.') if s.strip()]
        
        similar_pairs = []
        for s1 in sentences1:
            for s2 in sentences2:
                ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
                if ratio >= threshold and s1 != s2:
                    similar_pairs.append({
                        '이전 문장': s1,
                        '현재 문장': s2,
                        '유사도': f"{ratio:.2%}"
                    })
        
        return similar_pairs

    def get_diff_highlights(
        self, 
        text1: str, 
        text2: str
    ) -> Tuple[List[str], List[str]]:
        """두 텍스트 간의 차이점 하이라이트"""
        d = difflib.Differ()
        diff = list(d.compare(text1.splitlines(), text2.splitlines()))
        
        added = [line[2:] for line in diff if line.startswith('+ ')]
        removed = [line[2:] for line in diff if line.startswith('- ')]
        
        return added, removed

    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """주요 키워드 추출"""
        # 불용어 목록
        stopwords = set(['은', '는', '이', '가', '을', '를', '의', '와', '과', '으로', '로'])
        
        # 단어 분리 및 카운트
        words = text.split()
        word_count = {}
        
        for word in words:
            word = re.sub(r'[^\w\s]', '', word)  # 특수문자 제거
            if word and word not in stopwords:
                word_count[word] = word_count.get(word, 0) + 1
        
        # 상위 키워드 추출
        sorted_words = sorted(
            word_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_words[:top_n]