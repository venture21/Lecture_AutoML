### **1. 필요한 라이브러리 설치**

먼저 Python 환경에 필요한 라이브러리를 설치해야 합니다. 가상 환경을 사용하는 것을 강력히 권장합니다.

터미널 또는 명령 프롬프트에서 다음 명령어를 실행하세요.

```
# 가상 환경 생성 (선택 사항이지만 권장)
python -m venv .venv

# 가상 환경 활성화
# Windows:
# .venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 필요한 라이브러리 설치
pip install streamlit google-generativeai
```


### **2. Google Gemini API Key 발급**

Google AI Studio 또는 Google Cloud Console에서 Gemini API Key를 발급받아야 합니다.

- **Google AI Studio:** [https://aistudio.google.com/](https://www.google.com/url?sa=E&q=https%3A%2F%2Faistudio.google.com%2F) 에서 'Get API key'를 클릭하여 쉽게 발급받을 수 있습니다. 개인 프로젝트나 테스트용으로 적합합니다.
    
- **Google Cloud Console:** 더 복잡한 설정이나 IAM 권한 관리가 필요한 경우 사용합니다.
    

발급받은 API Key를 잘 복사해 두세요. 이 키는 코드에 직접 넣지 않고 환경 변수나 Streamlit Secrets 기능을 사용하여 안전하게 관리하는 것이 좋습니다.


### **3. Streamlit 애플리케이션 코드 작성**

다음 Python 코드를 app.py와 같은 이름으로 저장합니다.

```
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
api_key = os.getenv("GEMINI_API_KEY")

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
         st.session_state.model = genai.GenerativeModel('gemini-pro')

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
```


### **4. 실행 환경 구성 (API Key 설정)**

API 키를 설정하는 두 가지 주요 방법이 있습니다. 코드에서는 환경 변수 방식을 기본으로 사용하고, Streamlit Secrets 방식도 주석으로 포함했습니다.

- **방법 1: 환경 변수 사용 (로컬 실행 시 권장)**
    
    - 터미널을 열고 앱을 실행하기 전에 GEMINI_API_KEY 환경 변수를 설정합니다.
        
    - **Windows (명령 프롬프트):**
        
        ```
        set GEMINI_API_KEY="YOUR_API_KEY"
        ```
        
        content_copydownload
        
        Use code [with caution](https://support.google.com/legal/answer/13505487).Bash
        
    - **Windows (PowerShell):**
        
        ```
        $env:GEMINI_API_KEY="YOUR_API_KEY"
        ```
        
        content_copydownload
        
        Use code [with caution](https://support.google.com/legal/answer/13505487).Bash
        
    - **macOS/Linux (Bash/Zsh):**
        
        ```
        export GEMINI_API_KEY="YOUR_API_KEY"
        ```
        
        content_copydownload
        
        Use code [with caution](https://support.google.com/legal/answer/13505487).Bash
        
    - "YOUR_API_KEY" 부분에 실제 발급받은 API 키를 입력합니다.
        
    - 이렇게 설정한 환경 변수는 현재 터미널 세션에서만 유효합니다. 영구적으로 설정하려면 시스템 설정을 변경해야 합니다.
        
- **방법 2: Streamlit Secrets 사용 (Streamlit Cloud 배포 시 필수, 로컬도 가능)**
    
    - app.py 파일이 있는 디렉토리에 .streamlit 이라는 폴더를 생성합니다. (숨김 폴더입니다)
        
    - .streamlit 폴더 안에 secrets.toml 이라는 파일을 생성합니다.
        
    - secrets.toml 파일을 열고 다음 내용을 추가합니다.
        
        ```
        GEMINI_API_KEY="YOUR_API_KEY"
        ```
        
        content_copydownload
        
        Use code [with caution](https://support.google.com/legal/answer/13505487).Toml
        
    - "YOUR_API_KEY" 부분에 실제 발급받은 API 키를 입력합니다.
        
    - 로컬에서 Streamlit Secrets를 사용하려면 streamlit 라이브러리가 설치된 환경에서 .streamlit 폴더와 secrets.toml 파일이 app.py와 같은 레벨 또는 부모 레벨에 있어야 합니다. 코드에서 st.secrets["GEMINI_API_KEY"] 부분을 활성화해야 합니다.


### **5. Streamlit 애플리케이션 실행**

API 키를 설정한 터미널에서 app.py 파일이 있는 디렉토리로 이동하여 다음 명령어를 실행합니다.

```
streamlit run app.py
```

content_copydownload

Use code [with caution](https://support.google.com/legal/answer/13505487).Bash

명령어를 실행하면 웹 브라우저가 열리면서 Streamlit 애플리케이션이 나타납니다. 만약 자동으로 열리지 않으면 터미널에 표시된 Local URL 주소로 접속하세요 (일반적으로 http://localhost:8501).

**추가 설명:**

- **st.session_state:** Streamlit 앱은 사용자 상호작용(버튼 클릭, 텍스트 입력 등)이 있을 때마다 스크립트 전체가 다시 실행됩니다. 이때 st.session_state를 사용하면 이전 실행에서 저장했던 변수나 객체의 상태를 유지할 수 있습니다. 여기서는 대화 기록(messages)과 Gemini chat 객체를 저장하는 데 사용됩니다.
    
- **대화 기록 (History):** st.session_state.messages 리스트에 사용자와 AI의 메시지를 순서대로 저장합니다. google-generativeai 라이브러리의 start_chat() 메서드는 history 매개변수를 통해 이전 대화 내용을 전달받아 맥락을 유지할 수 있도록 합니다.
    
- **st.chat_message 및 st.chat_input:** Streamlit 1.22.0 버전부터 추가된 채팅 인터페이스 전용 위젯입니다. 대화창 형태의 UI를 쉽게 만들 수 있습니다.
    
- **오류 처리:** API 통신 중 발생할 수 있는 오류를 try...except 블록으로 처리하여 사용자에게 오류 메시지를 표시합니다.
    

이 코드는 기본적인 Gemini 챗봇의 기능을 구현하며, Streamlit의 핵심 기능인 session_state를 사용하여 대화 맥락을 유지하는 방법을 보여줍니다. 필요에 따라 UI를 개선하거나, 모델 파라미터를 조정하거나, 추가 기능을 구현해 보세요.