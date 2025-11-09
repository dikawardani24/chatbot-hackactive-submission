import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
import system_prompts as sp

def clear_option():
    st.session_state.option = ""
def clear_input_other_lang():
    st.session_state.others_lang = ""
def get_specific_lang():
    lang = ""
    if option:
        lang = option
    if len(others_lang) > 0:
        lang = others_lang
    return lang

st.title("💬 Code Buddy")
st.caption("A simple and friendly learning how to code with Google's Gemini model")

with st.sidebar:
    st.subheader("Settings")
    google_api_key = st.text_input("Google AI API Key", type="password")
    reset_button = st.button("Reset Conversation", help="Clear all messages and start fresh")
    option = st.selectbox(
        "Choose your favorite programming language",
        ("", "Python", "Kotlin", "Javascript", "Java"),
        key="option",
        on_change=clear_input_other_lang,
    )
    others_lang = st.text_input(
        label="Please input your favorite programming language if none of them",
        on_change= clear_option,
        key="others_lang"
    )

if not google_api_key:
    st.info("Please add your Google AI API key in the sidebar to start chatting.", icon="🗝️")
    st.stop()

if ("agent" not in st.session_state) or (getattr(st.session_state, "_last_key", None) != google_api_key):
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=google_api_key,
            temperature=0.7
        )

        st.session_state.agent = create_react_agent(
            model=llm,
            tools=[],
            prompt=sp.ini_prompt
        )

        st.session_state._last_key = google_api_key
        st.session_state.pop("messages", None)
    except Exception as e:
        st.error(f"Invalid API Key or configuration error: {e}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if reset_button:
    st.session_state.pop("agent", None)
    st.session_state.pop("messages", None)
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Type your message here...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        messages = []
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        specific_lang = get_specific_lang()
        print(specific_lang)
        if specific_lang != "":
            messages.append("You only need to talk about " + option + " programming language.")
        response = st.session_state.agent.invoke({"messages": messages})
        if "messages" in response and len(response["messages"]) > 0:
            answer = response["messages"][-1].content
        else:
            answer = "I'm sorry, I couldn't generate a response."

    except ChatGoogleGenerativeAIError as e:
        answer = "I'm sorry, I couldn't generate a response because you've provided an Invalid Google Ai api Key. Please provide a valid one and try again"
    except Exception as e:
        answer = "I'm sorry, I couldn't generate a response. Please push Reset Conversation and try again."

    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})