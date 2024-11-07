# src/views/analytics_view.py
import streamlit as st
import plotly.express as px
from ..managers.analytics_manager import AnalyticsManager

class AnalyticsView:
    """프롬프트 분석 화면"""
    
    def __init__(self, analytics_manager: AnalyticsManager):
        self.manager = analytics_manager

    def render_analytics(self):
        """분석 화면 렌더링"""
        st.header("프롬프트 분석")
        
        self._render_creation_trends()
        self._render_model_usage()
        self._render_category_stats()
        self._render_user_contribution()

    def _render_creation_trends(self):
        """생성 추이 차트"""
        st.subheader("프롬프트 생성 추이")
        
        dates, counts = self.manager.get_creation_trends()
        if dates:
            fig = px.line(
                x=dates,
                y=counts,
                labels={'x': '날짜', 'y': '생성된 프롬프트 수'},
                title="일별 프롬프트 생성 수"
            )
            st.plotly_chart(fig)
        else:
            st.info("데이터가 없습니다.")

    def _render_model_usage(self):
        """모델 사용 통계"""
        st.subheader("모델별 사용 통계")
        
        stats = self.manager.get_model_usage_stats()
        if stats:
            fig = px.bar(
                x=list(stats.keys()),
                y=list(stats.values()),
                labels={'x': '모델', 'y': '사용 횟수'},
                title="모델별 사용 횟수"
            )
            st.plotly_chart(fig)
        else:
            st.info("데이터가 없습니다.")

    def _render_category_stats(self):
        """카테고리 통계"""
        st.subheader("카테고리별 통계")
        
        stats = self.manager.get_category_stats()
        if stats:
            fig = px.pie(
                values=list(stats.values()),
                names=list(stats.keys()),
                title="카테고리별 분포"
            )
            st.plotly_chart(fig)
        else:
            st.info("데이터가 없습니다.")

    def _render_user_contribution(self):
        """사용자 기여도 통계"""
        st.subheader("사용자별 기여도")
        
        stats = self.manager.get_user_contribution_stats()
        if stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 프롬프트 생성 수")
                st.bar_chart(stats['prompt_count'])
            
            with col2:
                st.markdown("##### 베스트 프롬프트 수")
                st.bar_chart(stats['best_prompts'])
        else:
            st.info("데이터가 없습니다.")