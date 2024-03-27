import streamlit as st
from util.model import Model
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Chatbot", page_icon="🤖")

st.title("Chatbot 🤖")
st.header("Upload documents", divider='rainbow')

model_id: str = os.getenv("MODEL_PATH")
max_new_tokens: int = int(os.getenv("TOKEN_LIMIT"))
model: Model = Model.get(model_id, max_new_tokens)

if "messages" not in st.session_state:
    st.session_state["messages"] = list[dict[str, str]]()

messages: list[dict[str, str]] = st.session_state["messages"]

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        output = model.prompt(messages, prompt)
        response = st.markdown(output)

