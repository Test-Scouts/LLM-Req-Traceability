import streamlit as st
import os
from dotenv import load_dotenv
from helper import *
from torch import bfloat16
import transformers
from util.model import Model


load_dotenv()

st.set_page_config(page_title="REST-at", page_icon="🔍")

#==================================================
#                  Upload files
#================================================== 
st.title('Prototype - REST-at ✍️')
st.header("Upload documents",divider='rainbow')

# Create two columns layout


# Upload requirement file
re_file_content = upload_file('Requirment file', 'code_file')

# Checkbox to show or hide the Python code file content

if st.checkbox('Show RE content'):
    st.text('Requirement File Content:')
    st.code(re_file_content, language='text')

# Upload test suite file
test_file_content = upload_file('Test Cases File', 'test_file')

# Checkbox to show or hide the Python test file content
if st.checkbox('Show Test Cases content'):
    st.text('Test Case File Content:')
    st.code(test_file_content, language='text')


#==================================================
#                  CSV PARSE
#================================================== 

if st.checkbox('Requirement CVS parse'):   
    rows = parse_and_display_csv(re_file_content)
    if rows:
        for r in rows:
            st.write(r)  # Display each row in the Streamlit app
    else:
        st.warning("No file content provided.")

if st.checkbox('Test CVS parse'):   
    rows = parse_and_display_csv(test_file_content)
    if rows:
        for r in rows:
            st.write(r)  # Display each row in the Streamlit app
    else:
        st.warning("No file content provided.")

#==================================================
#                  Model section
#==================================================


def interact_with_model() -> None:
    st.header("Model Interaction", divider="rainbow")

    model_id: str = os.getenv("MODEL_PATH")
    max_new_tokens: int = int(os.getenv("TOKEN_LIMIT"))
    model: Model = Model.load(model_id, max_new_tokens)

    if "message_history" not in st.session_state:
        st.session_state["message_history"] = list[dict[str, str]]()

    messages: list[dict[str, str]] = st.session_state["message_history"]

    chat = st.empty()
    history = chat.container()

    # Render chat history
    for message in messages:
        history.write(f"### {message['role'].title()}\n{message['content']}")

    input_field = st.empty()
    input_container = input_field.container()

    user_prompt: str = input_container.text_input("Input", key="text-input")

    # Ignore the rest if the send button isn't clicked
    if not input_container.button("Send"):
        return

    # Disable Input field
    input_field.empty()
    input_container = input_field.container()
    input_container.text_input("Input", key="text-input-disabled", disabled=True)
    input_container.button("Send", key="send-disabled", disabled=True)

    # Render new input
    history.write(f"### User\n{user_prompt}")

    # Clear message history if wanted
    if user_prompt.lower() == "clear":
        messages = []
        return

    # model.prompt(messages, user_prompt)
    res: str = model.prompt(messages, user_prompt)

    # Render response
    history.write(f"### Assistant\n{res}")

    st.rerun()


interact_with_model()
