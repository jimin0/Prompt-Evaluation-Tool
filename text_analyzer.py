# text_analyzer.py
import difflib

class TextAnalyzer:
    @staticmethod
    def count_stats(text):
        if not text:
            return {}
        
        return {
            '전체 글자 수': len(text),
            '공백 제외 글자 수': len(text.replace(' ', '')),
            '단어 수': len(text.split()),
            '줄 수': len(text.splitlines()),
            '문장 수': len([s for s in text.split('.') if s.strip()])
        }
    
    @staticmethod
    def find_similar_sentences(text1, text2, threshold=0.8):
        if not text1 or not text2:
            return []
            
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
                        '유사도': round(ratio * 100, 2)
                    })
        
        return similar_pairs
    
    @staticmethod
    def get_diff_highlights(text1, text2):
        if not text1 or not text2:
            return [], []
            
        d = difflib.Differ()
        diff = list(d.compare(text1.splitlines(), text2.splitlines()))
        
        added = [line[2:] for line in diff if line.startswith('+ ')]
        removed = [line[2:] for line in diff if line.startswith('- ')]
        
        return added, removed