import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 API 키 가져오기
# Streamlit Cloud에 배포할 경우, st.secrets 사용을 권장합니다.
# https://docs.streamlit.io/develop/concepts/secrets
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    st.error("환경 변수에 'GOOGLE_API_KEY'가 설정되지 않았습니다. .env 파일을 확인하거나 Streamlit Cloud Secrets를 사용하세요.")
else:
    # Gemini API 구성
    genai.configure(api_key=google_api_key)

    # Gemini 모델 초기화 (사용 가능한 모델 확인 후 적절한 모델 사용)
    # 예시: 'gemini-pro' 또는 다른 사용 가능한 모델
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
    except Exception as e:
        st.error(f"Gemini 모델 초기화 오류: {e}")
        st.warning("사용 가능한 모델 목록을 확인하고 'genai.GenerativeModel()'에 올바른 모델 이름을 입력해주세요.")
        st.stop() # 오류 발생 시 앱 실행 중지

    st.title("Gemini와 대화하기")

    # 이전 대화 기록을 저장할 세션 상태 변수 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 대화 기록 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력
    prompt = st.chat_input("무엇이든 물어보세요!")

    if prompt:
        # 사용자 입력 표시
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        try:
            # Gemini 모델 호출
            # chat = model.start_chat(history=st.session_state.messages) # 대화 기록을 사용하는 경우
            response = model.generate_content(prompt) # 간단한 질답의 경우

            # 모델 응답 표시
            with st.chat_message("assistant"):
                st.markdown(response.text)

            st.session_state.messages.append({"role": "assistant", "content": response.text})

        except Exception as e:
            st.error(f"Gemini 응답 생성 중 오류 발생: {e}")