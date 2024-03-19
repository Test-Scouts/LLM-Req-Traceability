import streamlit as st
import os
import json

def get_display_style():
    # Define the CSS style
    style = """
    <style>
    .padded {
        border: 2px solid #f0f2f6;            /* Light grey border */
        border-radius: 5px;                    /* Rounded corners */
        padding: 20px;                         /* Padding around the text */
        margin: 10px 0;                        /* Some margin for spacing */
        background-color: #f0f2f6;             /* Light grey background */
        font-family: monospace;                /* Monospace font for the template */
        word-wrap: break-word;                 /* Ensure long words do not overflow */
        max-width: 100%;                       /* Max width to prevent overly wide stretches */
        overflow-wrap: break-word;             /* Ensure the content wraps to prevent overflow */
        box-sizing: border-box;                /* Include padding and border in the element's total width and height */
    }
    </style>
    """
    return style 

def save_templates(templates):
    file_path = "prompt_templates.json"
    with open(file_path, "w") as file:
        json.dump(templates, file, indent=4)

def initialize_prompt_templates():
    file_path = "prompt_templates.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
                if not all(isinstance(item, dict) for item in data):
                    raise ValueError("Data is not in the expected format (list of dictionaries).")
                prompt_templates = data
            except (json.JSONDecodeError, ValueError) as e:
                st.error(f"Failed to load templates: {e}")
                prompt_templates = []
    else:
        prompt_templates = []
    return prompt_templates



def upload_file(file_type='', file_description='file', widget_name='widget_name'):
    # Generate a unique key based on file type and description
    widget_key = f"{widget_name}_file_uploader"
    
    st.write(f"Upload or drag and drop a {file_type} {file_description} below.")
    uploaded_file = st.file_uploader(f"Upload a {file_type} {file_description} here:", 
                                     type=None, label_visibility="collapsed", key=widget_key)
    if uploaded_file is not None:
        return uploaded_file.getvalue().decode("utf-8")
    return None

