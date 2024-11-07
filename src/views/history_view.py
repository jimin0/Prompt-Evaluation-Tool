import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional
from ..managers.history_manager import HistoryManager

class HistoryView:
    """프롬프트 히스토리 조회 화면"""
    
    def __init__(self, history_manager: HistoryManager):
        self.manager = history_manager

    def render_history(self):
        """히스토리 화면 렌더링"""
        st.header("프롬프트 히스토리")
        
        # 필터 섹션
        with st.expander("필터 옵션", expanded=True):
            filters = self._render_filters()
        
        # 히스토리 데이터 조회
        history = self.manager.get_history(filters)
        
        if not history.empty:
            # 데이터 표시 옵션
            display_options = self._render_display_options()
            
            # 선택된 컬럼만 표시
            if display_options['columns']:
                history = history[display_options['columns']]
            
            # 정렬
            if display_options['sort_by']:
                history = history.sort_values(
                    by=display_options['sort_by'],
                    ascending=display_options['sort_ascending']
                )
            
            # 데이터 표시
            st.dataframe(
                history,
                use_container_width=True,
                height=display_options['height']
            )
            
            # 내보내기 옵션
            self._render_export_options(history)
            
            # 통계 정보
            self._render_stats(history)
        else:
            st.info("조회된 데이터가 없습니다.")

    def _render_filters(self) -> Dict:
        """필터 옵션 렌더링"""
        filters = {}
        
        # 레이아웃 구성
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 모델 필터
            model_filter = st.multiselect(
                "모델",
                options=["클로드", "GPT-3.5", "기타"],
                placeholder="모델 선택"
            )
            if model_filter:
                filters['model'] = model_filter
            
            # 버전 입력
            version_filter = st.text_input(
                "버전",
                placeholder="예: 1.0.0"
            )
            if version_filter:
                filters['version'] = version_filter
        
        with col2:
            # 카테고리 필터
            category_filter = st.multiselect(
                "카테고리",
                options=["법률", "사내규정", "금융", "기타"],
                placeholder="카테고리 선택"
            )
            if category_filter:
                filters['category'] = category_filter
            
            # 태그 필터
            tags_filter = st.text_input(
                "태그",
                placeholder="쉼표로 구분"
            )
            if tags_filter:
                filters['tags'] = [tag.strip() for tag in tags_filter.split(',')]
        
        with col3:
            # 날짜 범위 필터
            date_range = st.date_input(
                "날짜 범위",
                value=(
                    datetime.now() - timedelta(days=30),
                    datetime.now()
                )
            )
            if len(date_range) == 2:
                filters['date_range'] = date_range
            
            # 생성자 필터
            creator_filter = st.text_input(
                "생성자",
                placeholder="생성자 이름"
            )
            if creator_filter:
                filters['created_by'] = creator_filter
        
        return filters

    def _render_display_options(self) -> Dict:
        """표시 옵션 렌더링"""
        options = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 표시할 컬럼 선택
            options['columns'] = st.multiselect(
                "표시할 컬럼",
                options=[
                    "title", "model", "version", "category",
                    "created_by", "created_at", "is_best"
                ],
                default=["title", "model", "version", "created_at"]
            )
            
            # 테이블 높이 설정
            options['height'] = st.slider(
                "테이블 높이",
                min_value=200,
                max_value=800,
                value=400,
                step=50
            )
        
        with col2:
            # 정렬 옵션
            options['sort_by'] = st.selectbox(
                "정렬 기준",
                options=["created_at", "title", "version"],
                index=0
            )
            
            options['sort_ascending'] = st.checkbox(
                "오름차순 정렬",
                value=False
            )
        
        return options

    def _render_export_options(self, data: pd.DataFrame):
        """내보내기 옵션 렌더링"""
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.selectbox(
                "내보내기 형식",
                options=['CSV', 'Excel', 'JSON']
            )
        
        with col2:
            if st.button("내보내기"):
                try:
                    file_data = self.manager.export_history(
                        data,
                        export_format.lower()
                    )
                    
                    file_name = f"prompt_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    file_extension = export_format.lower()
                    
                    st.download_button(
                        f"{export_format} 다운로드",
                        file_data,
                        f"{file_name}.{file_extension}",
                        mime=self._get_mime_type(export_format)
                    )
                    
                except Exception as e:
                    st.error(f"내보내기 중 오류가 발생했습니다: {str(e)}")

    def _get_mime_type(self, format: str) -> str:
        """형식별 MIME 타입 반환"""
        mime_types = {
            'CSV': 'text/csv',
            'Excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'JSON': 'application/json'
        }
        return mime_types.get(format, 'text/plain')

    def _render_stats(self, data: pd.DataFrame):
        """통계 정보 렌더링"""
        with st.expander("통계 정보", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("총 프롬프트 수", len(data))
                st.metric("베스트 프롬프트 수", len(data[data['is_best']]))
            
            with col2:
                model_counts = data['model'].value_counts()
                st.write("모델별 분포")
                st.bar_chart(model_counts)
            
            with col3:
                category_counts = data['category'].value_counts()
                st.write("카테고리별 분포")
                st.bar_chart(category_counts)
