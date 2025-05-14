
### **1. 필요한 라이브러리 설치**

먼저 터미널이나 명령 프롬프트에서 필요한 라이브러리를 설치합니다.

```
pip install streamlit google-generativeai python-dotenv
```


### **2. .env 파일 생성**

프로젝트의 루트 디렉토리(Streamlit 코드를 저장할 폴더)에 .env 파일을 생성합니다. 이 파일에 Gemini API 키를 저장하여 코드에 직접 노출되지 않도록 합니다.

.env 파일 내용:

```
GOOGLE_API_KEY=여러분의_GEMINI_API_KEY
```

여러분의_GEMINI_API_KEY 부분에는 발급받은 실제 Gemini API 키를 넣어주세요.

**주의:** .env 파일은 절대 공개된 저장소(예: GitHub)에 커밋하지 마세요. .gitignore 파일에 .env를 추가하여 추적되지 않도록 설정하는 것이 좋습니다.


### **3. Streamlit 애플리케이션 코드 작성**

app2.py와 같이 적절한 이름으로 파이썬 파일을 생성하고 아래 코드를 복사하여 붙여넣습니다.

```
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
        model = genai.GenerativeModel('gemini-pro')
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
```

### **4. 실행 환경 구성 및 실행 방법**

1. **프로젝트 폴더 생성:** Streamlit 앱과 .env 파일을 저장할 폴더를 생성합니다.
    
2. **파일 저장:** 위에서 작성한 app.py 파일과 .env 파일을 생성한 폴더에 저장합니다. .env 파일에는 발급받은 Gemini API 키를 정확히 입력했는지 다시 확인합니다.
    
3. **터미널 열기:** 생성한 프로젝트 폴더로 터미널 또는 명령 프롬프트를 이동합니다.
    
4. **Streamlit 앱 실행:** 다음 명령어를 입력하여 Streamlit 애플리케이션을 실행합니다.
    
    ```
    streamlit run app2.py
    ```
    
    이 명령을 실행하면 웹 브라우저가 자동으로 열리면서 Streamlit 애플리케이션이 나타납니다.