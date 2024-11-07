# app.py
import streamlit as st
from prompt_manager import PromptManager
from user_manager import UserManager

class App:
    def __init__(self):
        st.set_page_config(page_title="프롬프트 관리 도구", layout="wide")
        
        if 'user_manager' not in st.session_state:
            st.session_state.user_manager = UserManager()
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
            
        self.prompt_manager = PromptManager()
        self.user_manager = st.session_state.user_manager
    
    def render_user_sidebar(self):
        st.sidebar.title("사용자 관리")
        
        # 기존 사용자 선택
        users = self.user_manager.get_all_users()
        if not users.empty:
            selected_user = st.sidebar.selectbox(
                "기존 사용자 선택",
                options=users['username'].tolist(),
                index=None
            )
            if selected_user:
                user_info = users[users['username'] == selected_user].iloc[0]
                st.session_state.current_user = {
                    'username': user_info['username']
                }
        
        # 새 사용자 등록
        st.sidebar.markdown("---")
        st.sidebar.subheader("새 사용자 등록")
        with st.sidebar.form("new_user_form"):
            new_username = st.text_input("이름")
            
            submit = st.form_submit_button("등록")
            if submit and new_username:
                success, message = self.user_manager.save_user(new_username)
                if success:
                    st.sidebar.success(message)
                else:
                    st.sidebar.error(message)
    
    def run(self):
        st.title("프롬프트 관리 도구")
        
        # 사용자 관리 사이드바 렌더링
        self.render_user_sidebar()
        
        # 메인 메뉴
        st.sidebar.markdown("---")
        st.sidebar.title("메뉴")
        menu = st.sidebar.selectbox(
            "메뉴 선택",
            ["새 프롬프트 작성", "프롬프트 히스토리", "버전 비교", 
             "일관성 테스트", "프롬프트 검색", "분석 대시보드"]
        )
        
        # 현재 사용자 표시
        if st.session_state.current_user:
            st.markdown(f"""**현재 사용자**: {st.session_state.current_user['username']}""")
        else:
            st.warning("사용자를 선택하거나 등록해주세요.")
            return
        
        # 메뉴 렌더링
        if menu == "새 프롬프트 작성":
            self.prompt_manager.render_prompt_creation()
        elif menu == "프롬프트 히스토리":
            self.prompt_manager.render_history_view()
        elif menu == "버전 비교":
            self.prompt_manager.render_version_comparison()
        elif menu == "일관성 테스트":
            self.prompt_manager.render_consistency_test()
        elif menu == "분석 대시보드":
            self.prompt_manager.render_analytics()
        elif menu == "프롬프트 검색":
            self.prompt_manager.render_prompt_search()

if __name__ == "__main__":
    app = App()
    app.run()