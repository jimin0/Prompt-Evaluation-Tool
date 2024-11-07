# src/views/consistency_test_view.py
import streamlit as st
from ..managers.test_manager import TestManager

class ConsistencyTestView:
    """프롬프트 일관성 테스트 화면"""
    
    def __init__(self, test_manager: TestManager):
        self.manager = test_manager

    def render_test_form(self):
        """테스트 폼 렌더링"""
        st.header("프롬프트 일관성 테스트")
        
        prompt = st.text_area(
            "테스트할 프롬프트를 입력하세요",
            height=200,
            help="테스트하고자 하는 프롬프트 템플릿을 입력하세요."
        )
        
        test_cases = st.text_area(
            "테스트 케이스를 입력하세요 (각 줄에 하나씩)",
            height=100,
            help="각 줄에 하나의 테스트 케이스를 입력하세요."
        )
        
        if st.button("테스트 실행"):
            if not prompt:
                st.warning("프롬프트를 입력해주세요.")
                return
                
            if not test_cases:
                st.warning("테스트 케이스를 입력해주세요.")
                return
            
            # 테스트 케이스 전처리
            test_list = [case.strip() for case in test_cases.split('\n') if case.strip()]
            
            # 테스트 실행
            results = self.manager.run_consistency_test(prompt, test_list)
            
            # 결과 표시
            st.subheader("테스트 결과")
            for i, result in enumerate(results, 1):
                with st.expander(f"테스트 케이스 {i}"):
                    st.write("입력:", result['input'])
                    st.write("결과:")
                    st.code(result['combined_prompt'])
                    
                    st.write("통계:")
                    for key, value in result['stats'].items():
                        st.text(f"{key}: {value}")