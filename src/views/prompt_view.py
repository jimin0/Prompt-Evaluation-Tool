# src/views/prompt_view.py
import streamlit as st
from typing import Dict, Optional
from src.managers.prompt_manager import PromptManager

class PromptView:
    """프롬프트 생성 및 편집 화면"""
    
    def __init__(self, prompt_manager: PromptManager):
        self.manager = prompt_manager
        self.form_data = {}

    def render_creation_form(self):
        """프롬프트 생성 폼 렌더링"""
        st.header("새 프롬프트 작성")
        
        with st.form("prompt_form"):
            # 기본 정보 섹션
            self.form_data.update(self._render_basic_info())
            
            # 프롬프트 내용 섹션
            self.form_data.update(self._render_content_fields())
            
            # 평가 섹션
            self.form_data.update(self._render_evaluation_fields())
            
            submitted = st.form_submit_button("저장")
            if submitted:
                self._handle_submit()


    def _render_basic_info(self) -> Dict[str, str]:
        """기본 정보 필드 렌더링"""
        # 제목
        title = st.text_input("프롬프트 제목", placeholder="프롬프트의 제목을 입력하세요.")
        
        col1, col2 = st.columns(2)
        with col1:
            model = st.selectbox("모델 선택", ["클로드", "GPT-3.5", "기타"])
            version = st.text_input(
                "버전 번호", 
                value=st.session_state.get('current_version', "1.0.0")
            )
        
        with col2:
            category = st.selectbox("카테고리", ["법률", "사내규정", "금융", "기타"])
            tags = st.text_input("태그 (쉼표로 구분)")

        description = st.text_area(
            "프롬프트 설명",
            placeholder="프롬프트의 목적과 기대효과를 설명해주세요",
            height=100
        )
        
        return {
            "title": title,
            "model": model,
            "version": version,
            "category": category,
            "tags": tags,
            "description": description
        }

    def _render_content_fields(self) -> Dict[str, str]:
        """프롬프트 내용 필드 렌더링"""
        query = st.text_area("쿼리 입력")
        prompt_content = st.text_area("프롬프트 내용", height=200)
        chatbot_response = st.text_area("챗봇 답변", height=200)
        expected_result = st.text_area(
            "기대결과",
            placeholder="이 프롬프트를 통해 얻고자 하는 결과를 구체적으로 설명해주세요",
            height=150
        )
        
        return {
            "query": query,
            "prompt_content": prompt_content,
            "chatbot_response": chatbot_response,
            "expected_result": expected_result
        }

    def _render_evaluation_fields(self) -> Dict[str, any]:
        """평가 관련 필드 렌더링"""
        col1, col2 = st.columns(2)
        with col1:
            is_best = st.checkbox("베스트 답변")
            auto_increment = st.checkbox("버전 자동 증가", value=True)

        changes = st.text_area("변경 사항")
        improvements = st.text_area("개선사항")
        pros = st.text_area("장점")
        cons = st.text_area("단점")
        
        return {
            "is_best": is_best,
            "auto_increment": auto_increment,
            "changes": changes,
            "improvements": improvements,
            "pros": pros,
            "cons": cons
        }

    def _validate_form(self) -> bool:
        """폼 유효성 검사"""
        if not self.form_data.get('title'):
            st.error("제목을 입력해주세요.")
            return False
            
        if not self.form_data.get('version'):
            st.error("버전을 입력해주세요.")
            return False
            
        if not self.manager.validate_version(self.form_data.get('version', '')):
            st.error("올바른 버전 형식이 아닙니다. (예: 1.0.0)")
            return False
            
        if not self.form_data.get('prompt_content'):
            st.error("프롬프트 내용을 입력해주세요.")
            return False
            
        return True
    
    def _handle_submit(self):
        """폼 제출 처리"""
        if not self._validate_form():
            return
        
        try:
            # auto_increment는 UI용 옵션이므로 저장 데이터에서 제외
            save_data = {k: v for k, v in self.form_data.items() if k != 'auto_increment'}
            
            # 현재 사용자 정보 추가
            save_data.update({
                "created_by": st.session_state.current_user['username'],
                "department": st.session_state.current_user['department'],
                "user_role": st.session_state.current_user['role']
            })
            
            # 프롬프트 저장
            prompt_id = self.manager.create_prompt(save_data)
            
            # 자동 버전 증가 처리
            if self.form_data.get('auto_increment'):
                new_version = self.manager.increment_version(self.form_data['version'])
                st.session_state.current_version = new_version
            
            st.success("프롬프트가 성공적으로 저장되었습니다!")
        except Exception as e:
            st.error(f"저장 중 오류가 발생했습니다: {str(e)}")