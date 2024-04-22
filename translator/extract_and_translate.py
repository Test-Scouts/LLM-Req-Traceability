import random
import csv
import dotenv
import os
import argparse
import pandas as pd
import torch
from transformers import pipeline, StoppingCriteriaList, StoppingCriteria
import dotenv
import os

dotenv.load_dotenv()
# Set the device to use the GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
# Load the path to the model from the environment variables
model_path = os.getenv("AI_SWE-MODEL_PATH")

#flag - provide the number of requests to extract
#flag - the mapping header 

parser = argparse.ArgumentParser(description="Process file information.")
#Add arguments
parser.add_argument("--count", "-c", dest="count",type=int, default= 2, help="Number of extractions")
parser.add_argument("--dir", "-d", dest="directory",type=str, default="default", help="Directory to store the extracted files")
parser.add_argument("--map", "-m", dest="mapHeader",type=str,default='Rubrik', help="Mapping header for the extracted of test")
parser.add_argument("--test-name", "-tn", dest="st_name",type=str, default="ST", help="")
parser.add_argument("--req-name", "-rn", dest="req_name",type=str, default="RE", help="")

# Parse arguments
args = parser.parse_args()

directory_path = ""
if args.directory:
    directory_path = f"../src/GE-data-swe/extracted/{args.directory}/"
    os.makedirs(directory_path, exist_ok=True)
else:    
    directory_path = "../src/GE-data-swe/extracted/"
    os.makedirs(directory_path, exist_ok=True)


#Load the environment variables
req_amina:str = os.getenv("REQ_AMINA_CSV")
st_amina:str = os.getenv("ST_AMINA_CSV")

###################################################################
# AI Sweden Model Setup
# Using the configuration from huggingface: https://huggingface.co/AI-Sweden-Models/gpt-sw3-6.7b-v2-translator
# Date: 2024-04-22
###################################################################

# (Optional) - define a stopping criteria
# We ideally want the model to stop generate once the response from the Bot is generated
class StopOnTokenCriteria(StoppingCriteria):
    def __init__(self, stop_token_id):
        self.stop_token_id = stop_token_id

    def __call__(self, input_ids, scores, **kwargs):
        return input_ids[0, -1] == self.stop_token_id


pipe = pipeline(
    task="text-generation",
    model=model_path,
    device=device
)

stop_on_token_criteria = StopOnTokenCriteria(stop_token_id=pipe.tokenizer.bos_token_id)


###################################################################
# Translation Function
###################################################################
def translate_to_swedish(value):
    # This will translate English to Swedish
    # To translate from Swedish to English the prompt would be:
    prompt = f"<|endoftext|><s>User: Översätt till Engelska från Svenska\n{text}<s>Bot:"

    #prompt = f"<|endoftext|><s>User: Översätt till Svenska från Engelska\n{text}<s>Bot:"

    input_tokens = pipe.tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    max_model_length = 2048
    dynamic_max_length = max_model_length - input_tokens.shape[1]

    response = pipe(
        prompt,
        max_length=dynamic_max_length,
        truncation=True,
        stopping_criteria=StoppingCriteriaList([stop_on_token_criteria])
    )

    return response[0]["generated_text"].split("<s>Bot: ")[-1]

# Randomly select unique values from the csv file
def random_selection_unique_values(num_to_select:int ,max_row_in_csv:int):
    if num_to_select > max_row_in_csv + 1: 
        raise ValueError("Number of unique values to select exceeds the range of values.")
    
    random_list = set()
    while len(random_list) < num_to_select:
        random_list.add(random.randint(1, max_row_in_csv-2)) # zero is the headers
    sorted_list = sorted(list(random_list))
    return sorted_list


###################################################################
# CSV File Processing
###################################################################
#df is the DataFrame 
req_df = pd.read_csv(req_amina)
st_df = pd.read_csv(st_amina)


max_req:int = len(req_df)
num_to_extract:int = int(args.count) #number of requirements to extract
# Select random values from the csv file
choicen_req = random_selection_unique_values(num_to_extract, max_req)

# Extracting headers
req_headers = req_df.columns.tolist()
#print(req_headers)
st_headers = st_df.columns.tolist()
#print(st_headers)

# Extracting specific rows based on indices
req_df = req_df.iloc[choicen_req]
#print("Selected Rows:")
#print(selected_rows)

#Save Extracted RE to a csv file
req_file = f'{directory_path}{args.req_name}_extracted_{num_to_extract}.csv'
req_df.to_csv(req_file, index=False)
print("Saved extracted RE to a csv file")

req_IDdesc = req_df['Rubrik'].unique() #just to be sure that the are not duplicates
st_df = st_df[st_df['Rubrik'].isin(req_IDdesc)] #filter the ST based on the extracted RE

#Save Extracted ST to a csv file
st_file = f'{directory_path}{args.st_name}_extracted_{num_to_extract}.csv'
st_df.to_csv(st_file, index=False)
print("Saved extracted ST to a csv file")

###################################################################
# Translation process
###################################################################
# Iterate over each cell in the DataFrame and update it
def process_value(df):
    for column in df.columns:
        if column == 'ID':
            continue
        for index in df.index:
            original_value = df.at[index, column]
            new_value = translate_to_swedish(original_value)
            df.at[index, column] = new_value
    return df

###################################################################
# Translation and Saving
###################################################################
# Translate the extracted RE
print("Translating the extracted RE...")
req_df_translated = process_value(req_df)
traslated_req_file = f'{directory_path}{args.req_name}_translated_{num_to_extract}.csv'
print("Saving the translated RE")
req_df_translated.to_csv(traslated_req_file, index=False)

# Translate the extracted ST
print("Translating the extracted ST...")
st_df_translated = process_value(st_df)
traslated_st_file = f'{directory_path}{args.st_name}_translated_{num_to_extract}.csv'
print("Saving the translated ST")
st_df_translated.to_csv(traslated_st_file, index=False)

