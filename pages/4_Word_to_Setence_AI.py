import streamlit as st
from langchain.llms import OpenAI
import openai
import pandas as pd
import random

# Streamlit 페이지 타이틀 설정
st.title("🦜🔗 Word to Sentence")

# 사이드바 설정
with st.sidebar:
    # 사용자로부터 OpenAI API 키 입력받기
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    st.markdown("OpenAI API 키 받으러 가기 [여기 클릭](https://platform.openai.com/account/api-keys)")

# openai 라이브러리에 API 키 설정
if openai_api_key:
    openai.api_key = openai_api_key
    langchain_openai = OpenAI(api_key=openai_api_key)

# 웹에서 Excel 파일 불러오기
excel_url = "http://ewking.kr/AE/word_sentence.xlsx"  # URL 수정 확인
df = pd.read_excel(excel_url)


# 파일이 성공적으로 불러와졌는지 확인 후 단어 리스트 세션 상태 설정
if 'words' in df.columns:
    words_list = df['words'].dropna().tolist()
    random.shuffle(words_list)
    st.session_state['words_list'] = words_list
    st.session_state['learned_count'] = 0  # 학습 카운터를 세션 상태에 추가

def generate_sentence_with_word(word):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a conversation sentence generator."},
                {"role": "user", "content": f"Please create a short and simple sentence using the easy word '{word}'."}
            ]
        )
        english_sentence = response['choices'][0]['message']['content']

        translation_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator from English to Korean."},
                {"role": "user", "content": f"Translate this sentence into Korean: '{english_sentence}'"}
            ]
        )
        korean_translation = translation_response['choices'][0]['message']['content']

        return english_sentence, korean_translation
    except Exception as e:
        st.error(f"API 호출 중 오류가 발생했습니다: {e}")
        return None, None

if st.button("Restart"):
    st.session_state.pop('words_list', None)
    st.session_state['learned_count'] = 0  # 세션 카운터 리셋

if st.session_state.get('words_list'):
    random_word = st.session_state['words_list'].pop(0)
    st.session_state['learned_count'] += 1  # 학습한 단어 카운트 증가
    with st.spinner('문장 생성중...'):
        english_sentence, korean_translation = generate_sentence_with_word(random_word)
        if english_sentence and korean_translation:
            highlighted_english_sentence = english_sentence.replace(random_word, f'<strong>{random_word}</strong>')
            st.markdown(f'<p style="font-size: 20px; text-align: center;">{highlighted_english_sentence}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 20px; text-align: center;">{korean_translation}</p>', unsafe_allow_html=True)
            st.markdown(f'공부한 단어 수: {st.session_state["learned_count"]}')  # 학습한 단어 수 표시

if st.session_state['words_list']:
    if st.button("다음단어"):
        if not st.session_state['words_list']:
            st.markdown(f'<p style="background-color: #bffff2; padding: 10px;">모든 단어에 대한 문장을 생성했습니다.</p>', unsafe_allow_html=True)
            del st.session_state['words_list']
            st.session_state['learned_count'] = 0  # 학습 카운터 초기화
