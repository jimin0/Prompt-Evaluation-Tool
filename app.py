import streamlit as st
import difflib
import pandas as pd
from datetime import datetime
from collections import Counter

def count_text_stats(text):
    """텍스트의 통계 정보를 반환"""
    stats = {
        '전체 글자 수': len(text),
        '공백 제외 글자 수': len(text.replace(' ', '')),
        '단어 수': len(text.split()),
        '줄 수': len(text.splitlines()),
        '문장 수': len([s for s in text.split('.') if s.strip()])
    }
    return stats

def find_similar_sentences(text1, text2, threshold=0.8):
    """두 텍스트에서 유사한 문장들을 찾아 반환"""
    sentences1 = [s.strip() for s in text1.split('.') if s.strip()]
    sentences2 = [s.strip() for s in text2.split('.') if s.strip()]
    
    similar_pairs = []
    for s1 in sentences1:
        for s2 in sentences2:
            ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
            if ratio >= threshold and s1 != s2:
                similar_pairs.append({
                    '이전 문장': s1,
                    '현재 문장': s2,
                    '유사도': round(ratio * 100, 2)
                })
    
    return similar_pairs

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
        if old_prompt:
            stats_old = count_text_stats(old_prompt)
            st.markdown("##### 텍스트 통계")
            for key, value in stats_old.items():
                st.text(f"{key}: {value}")
        
    with col2:
        st.subheader("현재 버전")
        new_prompt = st.text_area("현재 버전 프롬프트를 입력하세요", height=200)
        if new_prompt:
            stats_new = count_text_stats(new_prompt)
            st.markdown("##### 텍스트 통계")
            for key, value in stats_new.items():
                st.text(f"{key}: {value}")
    
    similarity_threshold = st.slider(
        "문장 유사도 임계값 (%)", 
        min_value=50, 
        max_value=100, 
        value=80
    )
    
    if st.button("버전 비교"):
        if old_prompt and new_prompt:
            st.subheader("유사 문장 분석")
            similar_pairs = find_similar_sentences(
                old_prompt, 
                new_prompt, 
                threshold=similarity_threshold/100
            )
            
            if similar_pairs:
                df = pd.DataFrame(similar_pairs)
                st.dataframe(df)
            else:
                st.info("설정된 임계값 이상의 유사한 문장이 발견되지 않았습니다.")
            
            st.subheader("변경 사항")
            added, removed = get_diff_highlights(old_prompt, new_prompt)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### 제거된 내용")
                for line in removed:
                    st.markdown(f"- <span style='color: red'>{line}</span>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("##### 추가된 내용")
                for line in added:
                    st.markdown(f"- <span style='color: green'>{line}</span>", unsafe_allow_html=True)
            
            # 통계 비교
            if stats_old and stats_new:
                st.subheader("통계 변화")
                compare_df = pd.DataFrame({
                    '이전 버전': stats_old,
                    '현재 버전': stats_new,
                    '차이': {k: stats_new[k] - stats_old[k] for k in stats_old.keys()}
                }).transpose()
                st.dataframe(compare_df)
            
            # 변경 이력 저장
            if st.button("변경 이력 저장"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                history_data = {
                    "timestamp": [now],
                    "old_version": [old_prompt],
                    "new_version": [new_prompt],
                    "stats_comparison": [compare_df.to_dict()]
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