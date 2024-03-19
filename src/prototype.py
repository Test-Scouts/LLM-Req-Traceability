import streamlit as st
from helper import *


st.set_page_config(page_title="REST-at", page_icon="🔍")

#==================================================
#                  Upload files
#================================================== 
st.title('Prototype - REST-at 🔍👣')
st.header("Upload documents",divider='rainbow')

# Create two columns layout


# Upload Python code file

code_file_content = upload_file('Python code', 'py', 'code_file')

# Checkbox to show or hide the Python code file content

if st.checkbox('Show RE content'):
    st.text('Python Code File Content:')
    st.code(code_file_content, language='text')

# Upload Python test file

test_file_content = upload_file('Python test', 'py', 'test_file')

# Checkbox to show or hide the Python test file content

if st.checkbox('Show Test Cases content'):
    st.text('Python Test File Content:')
    st.code(test_file_content, language='text')

