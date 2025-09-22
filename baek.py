import streamlit as st
import google.generativeai as genai

# Streamlit secrets에서 API 키 가져오기
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except (KeyError, FileNotFoundError):
    st.error("🚨 Gemini API 키를 찾을 수 없습니다. .streamlit/secrets.toml에 추가해주세요.")
    st.stop()

# 모델 설정
model = genai.GenerativeModel('gemini-2.5-flash')

# Streamlit 페이지 설정
st.set_page_config(
    page_title="Gemini 챗봇 🤖",
    page_icon="🤖",
    layout="wide"
)

st.title("Gemini 2.5 Flash 챗봇 🤖")
st.caption("Streamlit과 Gemini API를 이용한 챗봇입니다.")

# 세션 상태(session_state) 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("무엇이든 물어보세요!"):
    # 사용자 메시지를 대화 기록에 추가하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 챗봇 응답 생성 및 표시
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 이전 대화를 포함하여 모델에 전달
        chat_session = model.start_chat(
            history=[
                {"role": message["role"], "parts": [message["content"]]}
                for message in st.session_state.messages[:-1] # 마지막 사용자 입력은 제외
            ]
        )
        
        try:
            response = chat_session.send_message(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"응답 생성 중 오류가 발생했습니다: {e}")
            full_response = "죄송합니다, 답변을 생성하는 데 문제가 발생했습니다."
            message_placeholder.markdown(full_response)
    
    # 챗봇 응답을 대화 기록에 추가
    st.session_state.messages.append({"role": "assistant", "content": full_response})