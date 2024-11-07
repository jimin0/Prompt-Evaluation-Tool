import streamlit as st
from src.database.database import PromptDatabase
from src.managers.prompt_manager import PromptManager
from src.managers.history_manager import HistoryManager
from src.managers.analytics_manager import AnalyticsManager
from src.managers.test_manager import TestManager
from src.views.prompt_view import PromptView
from src.views.history_view import HistoryView
from src.views.comparison_view import ComparisonView
from src.views.analytics_view import AnalyticsView
from src.utils.config import Config

def initialize_session_state():
    """세션 상태 초기화"""
    if 'database' not in st.session_state:
        st.session_state.database = PromptDatabase()
        st.session_state.database.create_tables()
    
    if 'config' not in st.session_state:
        st.session_state.config = Config()
    
    if 'current_version' not in st.session_state:
        st.session_state.current_version = st.session_state.config.get(
            'version.initial', 
            '1.0.0'
        )
    
    # 임시 사용자 정보 (실제 구현 시 로그인 시스템으로 대체)
    if 'current_user' not in st.session_state:
        st.session_state.current_user = {
            'username': '테스트 사용자',
            'department': '개발팀',
            'role': '관리자'
        }

def setup_page():
    """페이지 기본 설정"""
    st.set_page_config(
        page_title="프롬프트 관리 도구",
        page_icon="📝",
        layout="wide"
    )

def render_sidebar():
    """사이드바 렌더링"""
    with st.sidebar:
        st.title("프롬프트 관리 도구")
        
        # 사용자 정보 표시
        st.write(f"사용자: {st.session_state.current_user['username']}")
        st.write(f"부서: {st.session_state.current_user['department']}")
        st.write(f"역할: {st.session_state.current_user['role']}")
        
        st.markdown("---")
        
        # 메뉴 선택
        menu = st.selectbox(
            "메뉴 선택",
            options=[
                "프롬프트 작성",
                "프롬프트 히스토리",
                "버전 비교",
                "일관성 테스트",
                "분석 대시보드",
                "변경 이력"
            ]
        )
        
        st.markdown("---")
        
        # 버전 정보
        st.caption("v1.0.0")
        
        return menu

def initialize_managers():
    """매니저 객체 초기화"""
    database = st.session_state.database
    
    return {
        'prompt_manager': PromptManager(database),
        'history_manager': HistoryManager(database),
        'analytics_manager': AnalyticsManager(database),
        'test_manager': TestManager()
    }

def initialize_views(managers):
    """뷰 객체 초기화"""
    return {
        'prompt_view': PromptView(managers['prompt_manager']),
        'history_view': HistoryView(managers['history_manager']),
        'comparison_view': ComparisonView(managers['test_manager']),
        'analytics_view': AnalyticsView(managers['analytics_manager'])
    }

def main():
    """메인 애플리케이션"""
    try:
        # 기본 설정
        setup_page()
        
        # 세션 상태 초기화
        initialize_session_state()
        
        # 사이드바 렌더링 및 메뉴 선택
        selected_menu = render_sidebar()
        
        # 매니저 및 뷰 초기화
        managers = initialize_managers()
        views = initialize_views(managers)
        
        # 선택된 메뉴에 따른 화면 렌더링
        if selected_menu == "프롬프트 작성":
            views['prompt_view'].render_creation_form()
            
        elif selected_menu == "프롬프트 히스토리":
            views['history_view'].render_history()
            
        elif selected_menu == "버전 비교":
            views['comparison_view'].render_comparison()
            
        elif selected_menu == "일관성 테스트":
            st.header("프롬프트 일관성 테스트")
            managers['test_manager'].run_consistency_test()
            
        elif selected_menu == "분석 대시보드":
            views['analytics_view'].render_analytics()
            
        elif selected_menu == "변경 이력":
            st.header("변경 이력")
            history_data = managers['history_manager'].get_change_logs()
            
            if not history_data.empty:
                st.dataframe(history_data)
            else:
                st.info("변경 이력이 없습니다.")
        
    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
        if st.session_state.current_user['role'] == '관리자':
            st.exception(e)

if __name__ == "__main__":
    main()
