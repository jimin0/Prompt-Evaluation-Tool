import streamlit as st
from src.managers.analytics_manager import AnalyticsManager
import pandas as pd

class AnalyticsView:
    """프롬프트 분석 화면"""
    
    def __init__(self, analytics_manager: AnalyticsManager):
        self.manager = analytics_manager

    def render_analytics(self):
        """분석 화면 렌더링"""
        st.header("프롬프트 분석 대시보드")

        self._render_creation_trends()
        self._render_model_usage()
        self._render_category_stats()
        self._render_user_contribution()

    def _render_creation_trends(self):
        """생성 추이 차트"""
        st.subheader("프롬프트 생성 추이")
        dates, counts = self.manager.get_creation_trends()
        
        if dates and counts:
            chart_data = pd.DataFrame({
                'date': dates,
                'count': counts
            })
            st.line_chart(chart_data.set_index('date'))
        else:
            st.info("생성 추이 데이터가 없습니다.")

    def _render_model_usage(self):
        """모델 사용 통계"""
        st.subheader("모델별 사용 통계")
        stats = self.manager.get_model_usage_stats()
        
        if stats:
            chart_data = pd.DataFrame({
                'model': list(stats.keys()),
                'count': list(stats.values())
            })
            st.bar_chart(chart_data.set_index('model'))
        else:
            st.info("모델 사용 통계 데이터가 없습니다.")

    def _render_category_stats(self):
        """카테고리 통계"""
        st.subheader("카테고리별 통계")
        stats = self.manager.get_category_stats()
        
        if stats:
            chart_data = pd.DataFrame({
                'category': list(stats.keys()),
                'count': list(stats.values())
            })
            st.bar_chart(chart_data.set_index('category'))
        else:
            st.info("카테고리 통계 데이터가 없습니다.")

    def _render_user_contribution(self):
        """사용자 기여도 통계"""
        st.subheader("사용자별 기여도")
        stats = self.manager.get_user_contribution_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 프롬프트 생성 수")
            if stats['prompt_count']:
                chart_data = pd.DataFrame({
                    'user': list(stats['prompt_count'].keys()),
                    'count': list(stats['prompt_count'].values())
                })
                st.bar_chart(chart_data.set_index('user'))
            else:
                st.info("프롬프트 생성 데이터가 없습니다.")
        
        with col2:
            st.markdown("##### 베스트 프롬프트 수")
            if stats['best_prompts']:
                chart_data = pd.DataFrame({
                    'user': list(stats['best_prompts'].keys()),
                    'count': list(stats['best_prompts'].values())
                })
                st.bar_chart(chart_data.set_index('user'))
            else:
                st.info("베스트 프롬프트 데이터가 없습니다.")