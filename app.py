# app.py
import streamlit as st
from prompt_manager import PromptManager

class App:
    def __init__(self):
        st.set_page_config(page_title="프롬프트 관리 도구", layout="wide")
        self.prompt_manager = PromptManager()
    
    def run(self):
        st.title("프롬프트 관리 도구")
        
        menu = st.sidebar.selectbox(
            "메뉴 선택",
            ["새 프롬프트 작성", "프롬프트 히스토리", "버전 비교", 
             "일관성 테스트", "프롬프트 검색", "분석 대시보드"]
        )
        
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