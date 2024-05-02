import streamlit as st
from ..core.model import Session
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Chatbot", page_icon="🤖")

st.title("Chatbot 🤖")
st.header("Upload documents", divider='rainbow')

session_name: str = "chatbot"
model_id: str = os.getenv("MODEL_PATH")
max_new_tokens: int = int(os.getenv("TOKEN_LIMIT"))
session: Session = Session.create(session_name, model_id, max_new_tokens)

system_prompt: str = st.text_input("System Prompt")

if system_prompt:
    session.system_prompt = system_prompt
    session.clear()

messages: list[dict[str, str]] = session.history
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's up?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        output = session.prompt(prompt)
        response = st.markdown(output)

