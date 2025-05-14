import streamlit as st
import google.generativeai as genai
import os

# Streamlit 페이지 설정
st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖")
st.title("Gemini 챗봇 데모")
st.write("Google Gemini API를 사용하여 대화해 보세요.")

# --- API Key 설정 ---
# 방법 1: 환경 변수 사용 (로컬 실행 또는 일부 배포 환경)
# GEMINI_API_KEY 환경 변수에 API 키를 설정해야 합니다. (아래 "실행 환경 구성" 참고)
api_key = "여러분의 api key"
#api_key = os.getenv("GEMINI_API_KEY")

# 방법 2: Streamlit Secrets 사용 (Streamlit Cloud 배포 시 권장)
# .streamlit/secrets.toml 파일에 API 키를 설정해야 합니다. (아래 "실행 환경 구성" 참고)
# try:
#     api_key = st.secrets["GEMINI_API_KEY"]
# except KeyError:
#     api_key = None # 환경 변수나 secrets에 키가 없는 경우

# API 키가 없으면 오류 메시지 표시 및 실행 중지
if not api_key:
    st.error("Gemini API Key가 설정되지 않았습니다.")
    st.markdown("""
        API 키를 설정하는 방법은 다음과 같습니다:
        1. **환경 변수 사용 (로컬):** 터미널에서 `export GEMINI_API_KEY='YOUR_API_KEY'` 또는 `set GEMINI_API_KEY='YOUR_API_KEY'` 명령어를 실행하세요.
        2. **Streamlit Secrets 사용 (로컬 또는 Streamlit Cloud):** `.streamlit/secrets.toml` 파일을 만들고 `GEMINI_API_KEY="YOUR_API_KEY"` 형식으로 저장하세요.
        """)
    st.stop() # API 키가 없으면 여기서 중단

# Gemini 모델 설정
try:
    genai.configure(api_key=api_key)
    # 사용할 모델 지정 (예: gemini-pro)
    # 사용 가능한 모델 목록은 https://ai.google.dev/models 에서 확인하세요.
    if "model" not in st.session_state:
         st.session_state.model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')

except Exception as e:
    st.error(f"Gemini 모델 설정 중 오류 발생: {e}")
    st.stop()

# --- 대화 기록 관리 (st.session_state 사용) ---
# Streamlit은 페이지가 다시 로드될 때마다 스크립트를 처음부터 실행합니다.
# 따라서 대화 기록을 유지하기 위해 session_state에 저장해야 합니다.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Gemini chat 객체 관리
# chat 객체도 session_state에 저장하여 대화 맥락을 유지합니다.
if "chat" not in st.session_state:
     # messages에 저장된 이전 대화를 기반으로 새 chat 세션 시작
     st.session_state.chat = st.session_state.model.start_chat(history=st.session_state.messages)
# else: # 이미 chat 객체가 있다면, 해당 객체를 계속 사용합니다.

# --- 이전 대화 기록 표시 ---
# st.session_state.messages에 저장된 대화 기록을 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]): # 역할(user, assistant)에 따라 아이콘 표시
        st.markdown(message["content"]) # 메시지 내용 표시

# --- 사용자 입력 처리 ---
# st.chat_input은 채팅 인터페이스에 맞는 입력 위젯입니다.
if prompt := st.chat_input("여기에 메시지를 입력하세요..."):
    # 1. 사용자의 메시지를 대화 기록(messages)에 추가
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. 사용자의 메시지를 화면에 표시
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Gemini API에 메시지를 보내고 응답 받기
    with st.chat_message("assistant"):
        message_placeholder = st.empty() # 응답을 실시간으로 표시할 빈 공간
        try:
            # send_message 메서드로 메시지를 보내고 응답 받기
            # stream=True 옵션으로 응답을 스트리밍으로 받을 수 있으나, 여기서는 간단하게 False 사용
            response = st.session_state.chat.send_message(prompt)
            full_response = response.text # 응답 텍스트 가져오기

            # 4. Gemini의 응답을 대화 기록(messages)에 추가
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # 5. Gemini의 응답을 화면에 표시
            message_placeholder.markdown(full_response)

        except Exception as e:
            error_message = f"응답 생성 중 오류 발생: {e}"
            message_placeholder.error(error_message)
            # 오류 발생 시 마지막 사용자 메시지를 기록에서 제거 (선택 사항)
            st.session_state.messages.pop()
            st.session_state.messages.append({"role": "assistant", "content": error_message}) # 오류 메시지도 기록에 추가

# --- 앱 하단 정보 ---
st.sidebar.header("정보")
st.sidebar.write("이 앱은 Streamlit과 Google Gemini API를 사용하여 구축되었습니다.")
st.sidebar.write("[Google AI Studio](https://aistudio.google.com/)에서 API 키를 받을 수 있습니다.")