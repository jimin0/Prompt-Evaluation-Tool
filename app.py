import streamlit as st
import difflib
import pandas as pd
from datetime import datetime

def get_diff_highlights(text1, text2):
    """두 텍스트 간의 차이점을 찾아 HTML 형식으로 반환"""
    d = difflib.Differ()
    diff = list(d.compare(text1.splitlines(), text2.splitlines()))
    
    added = [line[2:] for line in diff if line.startswith('+ ')]
    removed = [line[2:] for line in diff if line.startswith('- ')]
    
    return added, removed

def test_prompt_consistency(prompt, test_cases):
    """프롬프트의 일관성을 테스트하고 결과를 반환"""
    results = []
    for test in test_cases:
        # 여기서는 예시로 단순히 프롬프트와 테스트 케이스를 합치지만,
        # 실제로는 이 부분에 AI 모델 호출 코드가 들어갈 수 있습니다
        result = f"{prompt}\n\nTest Input: {test}"
        results.append(result)
    return results

# Streamlit UI
st.title("프롬프트 버전 비교 및 테스트 도구")

# 사이드바에 메뉴 추가
menu = st.sidebar.selectbox(
    "메뉴 선택",
    ["프롬프트 버전 비교", "일관성 테스트"]
)

if menu == "프롬프트 버전 비교":
    st.header("프롬프트 버전 비교")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("이전 버전")
        old_prompt = st.text_area("이전 버전 프롬프트를 입력하세요", height=200)
        
    with col2:
        st.subheader("현재 버전")
        new_prompt = st.text_area("현재 버전 프롬프트를 입력하세요", height=200)
    
    if st.button("버전 비교"):
        if old_prompt and new_prompt:
            added, removed = get_diff_highlights(old_prompt, new_prompt)
            
            st.subheader("변경 사항")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 제거된 내용")
                for line in removed:
                    st.markdown(f"- <span style='color: red'>{line}</span>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("##### 추가된 내용")
                for line in added:
                    st.markdown(f"- <span style='color: green'>{line}</span>", unsafe_allow_html=True)
            
            # 변경 이력 저장
            if st.button("변경 이력 저장"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history_data = {
                    "timestamp": [now],
                    "old_version": [old_prompt],
                    "new_version": [new_prompt]
                }
                history_df = pd.DataFrame(history_data)
                history_df.to_csv(f"prompt_history_{now}.csv", index=False)
                st.success("변경 이력이 저장되었습니다!")

elif menu == "일관성 테스트":
    st.header("프롬프트 일관성 테스트")
    
    prompt = st.text_area("테스트할 프롬프트를 입력하세요", height=200)
    test_cases = st.text_area("테스트 케이스를 입력하세요 (각 줄에 하나씩)", height=100)
    
    if st.button("테스트 실행"):
        if prompt and test_cases:
            test_list = [case.strip() for case in test_cases.split('\n') if case.strip()]
            results = test_prompt_consistency(prompt, test_list)
            
            st.subheader("테스트 결과")
            for i, (test, result) in enumerate(zip(test_list, results)):
                with st.expander(f"테스트 케이스 {i+1}"):
                    st.write(f"입력: {test}")
                    st.write("결과:")
                    st.write(result)