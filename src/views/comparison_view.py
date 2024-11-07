# src/views/comparison_view.py
import streamlit as st
import pandas as pd
from typing import Dict
from ..managers.test_manager import TestManager

class ComparisonView:
    """프롬프트 버전 비교 화면"""
    
    def __init__(self, test_manager: TestManager):
        self.manager = test_manager

    def render_comparison(self):
        """비교 화면 렌더링"""
        st.header("프롬프트 버전 비교")
        
        # 비교 옵션
        similarity_threshold = st.slider(
            "유사도 임계값 (%)",
            min_value=50,
            max_value=100,
            value=80
        ) / 100
        
        # 프롬프트 입력
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("이전 버전")
            old_prompt = st.text_area(
                "이전 버전 프롬프트를 입력하세요",
                height=300,
                key="old_prompt"
            )
            
            if old_prompt:
                stats_old = self.manager.text_analyzer.count_stats(old_prompt)
                with st.expander("텍스트 통계"):
                    for key, value in stats_old.items():
                        st.text(f"{key}: {value}")
        
        with col2:
            st.subheader("현재 버전")
            new_prompt = st.text_area(
                "현재 버전 프롬프트를 입력하세요",
                height=300,
                key="new_prompt"
            )
            
            if new_prompt:
                stats_new = self.manager.text_analyzer.count_stats(new_prompt)
                with st.expander("텍스트 통계"):
                    for key, value in stats_new.items():
                        st.text(f"{key}: {value}")
        
        # 비교 실행
        if st.button("비교 분석"):
            if old_prompt and new_prompt:
                self._run_comparison(
                    old_prompt,
                    new_prompt,
                    similarity_threshold
                )
            else:
                st.warning("두 버전의 프롬프트를 모두 입력해주세요.")

    def _run_comparison(
        self,
        old_prompt: str,
        new_prompt: str,
        threshold: float
    ):
        """비교 분석 실행 및 결과 표시"""
        # 결과 얻기
        results = self.manager.compare_versions(
            old_prompt,
            new_prompt,
            similarity_threshold=threshold
        )
        
        # 통계 비교
        if results['old_stats'] and results['new_stats']:
            st.subheader("통계 변화")
            
            # DataFrame으로 변환하여 비교
            compare_df = pd.DataFrame({
                '이전 버전': results['old_stats'],
                '현재 버전': results['new_stats'],
                '차이': {
                    k: results['new_stats'][k] - results['old_stats'][k] 
                    for k in results['old_stats'].keys()
                }
            }).transpose()
            
            st.dataframe(compare_df)
        
        # 유사 문장 분석
        if results['similar_pairs']:
            st.subheader("유사 문장 분석")
            st.dataframe(
                pd.DataFrame(results['similar_pairs']),
                use_container_width=True
            )
        
        # 변경 사항
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("##### 제거된 내용")
            for line in results['removed_lines']:
                st.markdown(
                    f"- <span style='color: red'>{line}</span>",
                    unsafe_allow_html=True
                )
        
        with col4:
            st.markdown("##### 추가된 내용")
            for line in results['added_lines']:
                st.markdown(
                    f"- <span style='color: green'>{line}</span>",
                    unsafe_allow_html=True
                )
        
        # 구조 분석
        st.subheader("구조 분석")
        old_structure = self.manager.validate_prompt_structure(old_prompt)
        new_structure = self.manager.validate_prompt_structure(new_prompt)
        
        col5, col6 = st.columns(2)
        with col5:
            st.markdown("##### 이전 버전 구조")
            for key, value in old_structure.items():
                st.write(f"- {key}: {'✓' if value else '✗'}")
        
        with col6:
            st.markdown("##### 현재 버전 구조")
            for key, value in new_structure.items():
                st.write(f"- {key}: {'✓' if value else '✗'}")