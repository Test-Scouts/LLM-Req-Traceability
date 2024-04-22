import streamlit as st
import os
import json
from io import StringIO
import csv

# use in the previous prototype -- may be removed in the final version
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
# use in the previous prototype -- may be removed in the final version
def save_templates(templates):
    file_path = "prompt_templates.json"
    with open(file_path, "w") as file:
        json.dump(templates, file, indent=4)

# use in the previous prototype -- may be removed in the final version
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



def upload_file(file_description='file', widget_name='widget_name'):
    # Generate a unique key based on file type and description
    widget_key = f"{widget_name}_file_uploader"
    
    st.write(f"Upload or drag and drop a  {file_description} below.")
    uploaded_file = st.file_uploader(f"Upload a {file_description} here:", 
                                     type=None, label_visibility="collapsed", key=widget_key)
    
    if uploaded_file is not None:
        return uploaded_file.getvalue().decode("utf-8")
    return None


def parse_csv_to_json(file_content):
    """
    Parses CSV file_content from a string and displays it using Streamlit or returns parsed data.
    
    Parameters:
    - file_content (str): The CSV content as a string.
    
    Returns:
    - None. Directly displays the content using Streamlit.
    """
    if file_content:
        # Convert the string content to a file-like object for parsing
        f = StringIO(file_content)
        
        # Detect the CSV dialect
        try:
            dialect: csv.Dialect = csv.Sniffer().sniff(f.read(1024))
            f.seek(0)  # Reset file pointer to the beginning
        except csv.Error:
            st.error("Could not determine the file's dialect. Please ensure it is a valid CSV file.")
            return
        
        # Parse the CSV content into a dictionary format
        results: csv.DictReader = csv.DictReader(f, dialect=dialect)
        return results

def load_json_file(file_path):
    # Open the file in read mode ('r') and load its content using json.load
    with open(file_path, 'r') as file:
        results = json.load(file)

    return results