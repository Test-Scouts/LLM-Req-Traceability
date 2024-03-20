import streamlit as st

st.set_page_config(page_title="Prototype -Testing ground", page_icon="✍️")
st.title('Prototype V2  🔍👣')
st.header("Upload documents", divider='rainbow')

# Upload multiple files and store them in session state
uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True, type=None, key="uploaded_files")

if 'uploaded_file_names' not in st.session_state:
    st.session_state['uploaded_file_names'] = []
    st.session_state['uploaded_file_contents'] = []

if uploaded_files:
    # Reset session state for new uploads
    st.session_state['uploaded_file_names'] = []
    st.session_state['uploaded_file_contents'] = []
    for uploaded_file in uploaded_files:
        # Read the content of the uploaded file
        content = uploaded_file.getvalue().decode("utf-8")
        # Update session state with the new file's name and content
        st.session_state['uploaded_file_names'].append(uploaded_file.name)
        st.session_state['uploaded_file_contents'].append(content)

#==================================================
#                  Display Files
#================================================== 

st.subheader("Display Files", divider='rainbow')

# Initialize variables to prevent errors
selected_file_index = None
send_button = False

# Only proceed if there are uploaded files
if st.session_state['uploaded_file_names']:
    selected_file_name = st.selectbox("Choose a file to display", options=st.session_state['uploaded_file_names'])
    # Checkbox to decide if content should be displayed
    if st.checkbox('Show selected file content'):
        selected_file_index = st.session_state['uploaded_file_names'].index(selected_file_name)
        st.code(st.session_state['uploaded_file_contents'][selected_file_index], language='python')


#==================================================
#                  LLM
#================================================== 
"""
    # Point to the local server
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
    pre_prompt_default = "You are a helpful AI assistant."
    pre_prompt = st.text_area("Edit System-prompt", value=pre_prompt_default, key="edit_system_prompt")
    st.divider()
    send_button = st.button("Send to AI")

    if send_button and selected_file_index is not None:

    #--------------------------------------------------    
        # When a file is selected and the send button is pressed
        prompt = "I will provide you a python module, then a series of unit tests targeting that module. First, here is the python module:"
        #file = st.session_state['uploaded_file_contents'][selected_file_index]
        file = "empty file"
     #-------------------------------------------------- 
    
        filled_template = prompt + file
        completion = client.chat.completions.create(
            model="local-model",  # Placeholder for actual model name
            messages=[
                {"role": "system", "content": pre_prompt},
                {"role": "user", "content": filled_template}
            ],
            temperature=0.7,
        )

        # Display the completion result
        st.divider()
        st.markdown(completion.choices[0].message['content'])
else:
    st.write("No files uploaded yet or choose a file to display.")
"""