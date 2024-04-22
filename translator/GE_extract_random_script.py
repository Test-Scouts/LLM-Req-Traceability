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
parser.add_argument("--count", "-c", dest="count",type=int, help="Number of extractions")
parser.add_argument("--dir", "-d", dest="directory",type=str, help="Directory to store the extracted files")
parser.add_argument("--map", "-m", dest="mapping",type=str, help="Mapping header for the extracted of test")
parser.add_argument("--mode", "-mo", dest="mode",type=str, help="")

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
max_req:int = int(os.getenv("END_REQ")) #max number of requirements in the csv file
num_of_req:int = int(os.getenv("NUM_OF_REQ"))#number of requirements to extract

req_amina:str = os.getenv("REQ_AMINA_CSV")
st_amina:str = os.getenv("ST_AMINA_CSV")

###################################################################
# AI Sweden Model Setup
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
def translate_to_swedish(text):
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
        random_list.add(random.randint(0, max_row_in_csv-2))
    sorted_list = sorted(list(random_list))
    return sorted_list


###################################################################
# CSV File Processing
###################################################################
# Select random values from the csv file
choicen_req = random_selection_unique_values(num_of_req, max_req)

#print("\n".join([str(c) for c in choicen_req]))
#print("\n\n")

#df is the DataFrame 
df = pd.read_csv(req_amina)

# Extracting headers
headers = df.columns.tolist()
#print(headers)

# Extracting specific rows based on indices
selected_rows = df.iloc[choicen_req]
print("Selected Rows:")
print(selected_rows)

#Save Extracted RE to a csv file
req_file = f'{directory_path}{req_amina}_extracted_{num_of_req}.csv'
df.to_csv(req_file, index=False)


#Save Extracted ST to a csv file

###################################################################
# Translation process
###################################################################
# Iterate over each cell in the DataFrame and update it
for column in df.columns:
    for index in df.index:
        original_value = df.at[index, column]
        new_value = translate_to_swedish(original_value)
        df.at[index, column] = new_value


###################################################################
# Saving traslated version to a csv file
###################################################################




"""
TODO:
- store the values of the array in a file, so that we can append if necessary without 
    repeating the process.
    - create a function that will append to the existing values selected
    - OR create a function that can check that the existing values are not repeated
- map the values of the RE to the ST, using the "Rubrik" header as the key
    - extract the test headers and columns
- create two new csv files, one for the extracted RE and the other for the ST

SECOND TODO:
- translate the headers for RE and ST
- translate each cell in the rows
"""