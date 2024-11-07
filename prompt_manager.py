# prompt_manager.py
import streamlit as st
import pandas as pd
from text_analyzer import TextAnalyzer
from prompt_database import PromptDatabase

class PromptManager:
    def __init__(self):
        if 'database' not in st.session_state:
            st.session_state.database = PromptDatabase()
        if 'current_version' not in st.session_state:
            st.session_state.current_version = "1.0.0"
        
        self.text_analyzer = TextAnalyzer()
        self.database = st.session_state.database
        
    def render_prompt_creation(self):
        st.header("새 프롬프트 작성")
        
        with st.form("prompt_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                model = st.selectbox("모델 선택", ["클로드", "GPT-3.5", "기타"])
                version = st.text_input("버전 번호", value=st.session_state.current_version)
                
            with col2:
                category = st.selectbox("카테고리", ["법률", "사내규정", "금융", "기타"])
                tags = st.text_input("태그 (쉼표로 구분)")
                
            query = st.text_area("쿼리 입력")
            prompt_content = st.text_area("프롬프트 내용", height=200)
            chatbot_response = st.text_area("챗봇 답변", height=200)
            
            col3, col4 = st.columns(2)
            with col3:
                is_best = st.checkbox("베스트 답변")
                auto_increment = st.checkbox("버전 자동 증가", value=True)
                
            changes = st.text_area("변경 사항")
            improvements = st.text_area("개선사항")
            pros = st.text_area("장점")
            cons = st.text_area("단점")
            
            submitted = st.form_submit_button("저장")
            
            if submitted:
                self._save_prompt_data(
                    model, version, category, tags, query, prompt_content,
                    chatbot_response, is_best, changes, improvements, pros, cons,
                    auto_increment
                )
    
    def _save_prompt_data(self, model, version, category, tags, query, prompt_content,
                         chatbot_response, is_best, changes, improvements, pros, cons,
                         auto_increment):
        data = {
            "model": model,
            "version": version,
            "category": category,
            "tags": tags,
            "query": query,
            "prompt_content": prompt_content,
            "chatbot_response": chatbot_response,
            "is_best": is_best,
            "changes": changes,
            "improvements": improvements,
            "pros": pros,
            "cons": cons,
            "stats": str(self.text_analyzer.count_stats(prompt_content))
        }
        
        self.database.save_prompt(data)
        
        if auto_increment:
            major, minor, patch = map(int, version.split('.'))
            st.session_state.current_version = f"{major}.{minor}.{patch + 1}"
            
        st.success("프롬프트가 성공적으로 저장되었습니다!")
    
    def render_history_view(self):
        st.header("프롬프트 히스토리")
        
        history = self.database.get_history()
        
        if len(history) > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                model_filter = st.multiselect(
                    "모델 필터",
                    options=history['model'].unique()
                )
            with col2:
                version_filter = st.multiselect(
                    "버전 필터",
                    options=history['version'].unique()
                )
            with col3:
                category_filter = st.multiselect(
                    "카테고리 필터",
                    options=history['category'].unique()
                )
                
            filtered_df = history
            if model_filter:
                filtered_df = filtered_df[filtered_df['model'].isin(model_filter)]
            if version_filter:
                filtered_df = filtered_df[filtered_df['version'].isin(version_filter)]
            if category_filter:
                filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
                
            st.dataframe(filtered_df)
            
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "CSV 다운로드",
                csv,
                "prompt_history.csv",
                "text/csv"
            )
        else:
            st.info("저장된 프롬프트가 없습니다.")
    
    def render_version_comparison(self):
        st.header("프롬프트 버전 비교")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("이전 버전")
            old_prompt = st.text_area("이전 버전 프롬프트를 입력하세요", height=200)
            if old_prompt:
                stats_old = self.text_analyzer.count_stats(old_prompt)
                st.markdown("##### 텍스트 통계")
                for key, value in stats_old.items():
                    st.text(f"{key}: {value}")
        
        with col2:
            st.subheader("현재 버전")
            new_prompt = st.text_area("현재 버전 프롬프트를 입력하세요", height=200)
            if new_prompt:
                stats_new = self.text_analyzer.count_stats(new_prompt)
                st.markdown("##### 텍스트 통계")
                for key, value in stats_new.items():
                    st.text(f"{key}: {value}")

        if old_prompt and new_prompt and st.button("비교 분석"):
            similar_pairs = self.text_analyzer.find_similar_sentences(old_prompt, new_prompt)
            if similar_pairs:
                st.markdown("##### 유사 문장")
                st.dataframe(pd.DataFrame(similar_pairs))
                
            added, removed = self.text_analyzer.get_diff_highlights(old_prompt, new_prompt)
            
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("##### 제거된 내용")
                for line in removed:
                    st.markdown(f"- <span style='color: red'>{line}</span>", unsafe_allow_html=True)
            
            with col4:
                st.markdown("##### 추가된 내용")
                for line in added:
                    st.markdown(f"- <span style='color: green'>{line}</span>", unsafe_allow_html=True)
    
    def render_consistency_test(self):
        st.header("프롬프트 일관성 테스트")
        
        prompt = st.text_area("테스트할 프롬프트를 입력하세요", height=200)
        test_cases = st.text_area("테스트 케이스를 입력하세요 (각 줄에 하나씩)", height=100)
        
        if st.button("테스트 실행") and prompt and test_cases:
            test_list = [case.strip() for case in test_cases.split('\n') if case.strip()]
            
            st.subheader("테스트 결과")
            for i, test in enumerate(test_list, 1):
                with st.expander(f"테스트 케이스 {i}"):
                    st.write(f"입력: {test}")
                    st.write("결과:")
                    st.code(f"{prompt}\n\nTest Input: {test}")
    
    def render_analytics(self):
        st.header("프롬프트 분석")
        
        history = self.database.get_history()
        
        if len(history) > 0:
            st.subheader("프롬프트 생성 추이")
            history['date'] = pd.to_datetime(history['timestamp']).dt.date
            daily_counts = history.groupby('date').size()
            st.line_chart(daily_counts)
            
            st.subheader("모델별 사용 통계")
            model_counts = history['model'].value_counts()
            st.bar_chart(model_counts)
            
            st.subheader("카테고리별 통계")
            category_counts = history['category'].value_counts()
            st.bar_chart(category_counts)
    
    def render_prompt_search(self):
        st.header("프롬프트 검색")
        
        search_term = st.text_input("검색어 입력")
        if search_term:
            results = self.database.search(search_term)
            if len(results) > 0:
                st.dataframe(results)
            else:
                st.info("검색 결과가 없습니다.")