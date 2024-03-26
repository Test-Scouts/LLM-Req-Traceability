import streamlit as st
from helper import *
from torch import bfloat16
import transformers



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

st.header("Model Selection",divider='rainbow')
