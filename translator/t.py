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
import sys

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
parser.add_argument("--re-not-test", "-rnt", dest="without_test",type=int, default= 1, help="Number of requirements without test cases")
parser.add_argument("--one_re_to_many_test", "-otm", dest="one_to_many_test",type=int, default= 0, help="Number of requirements with at least two test cases")
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
###################################################################

# Empty

###################################################################
# Translation Function
###################################################################
def translate_to_swedish(value):
    #print("The org value is:",value)
    if isinstance(value, str):
        return "new: " + value
    
    if isinstance(value, float):
       # print("float:", value)
        value = int(value)
    if isinstance(value, int):
        #print("int",value)
        return value

def random_selection_and_filter(num_to_select: int, req_df: pd.DataFrame, st_df: pd.DataFrame, 
                                required_without_match: int, one_to_many_tests: int):
    if num_to_select > len(req_df):
        raise ValueError("Number of unique values to select exceeds the range of values.")
    
    selected_indices = set()
    count_without_match = 0
    count_double_st = 0
    num_of_visited_req = set() 

    # Track indices that fulfill the multiple ST requirement
    double_st_indices = set()
    # Example logic: at least 2 or as many as one_to_many_tests  
    min_st_per_req = 2 * one_to_many_tests  

    while len(selected_indices) < num_to_select:

        if len(num_of_visited_req) == len(req_df):
            print(f"All requirements have been visited. Nr of requiremts with multiple test cases are: {len(double_st_indices)}")
            sys.exit(1)

        # Randomly select an index
        random_index = random.randint(0, len(req_df) - 1)

        # Check if the index has already been visited
        if(random_index in num_of_visited_req):
            continue
        else:
            num_of_visited_req.add(random_index) # Add the index to the visited set

        rubrik_value = req_df.iloc[random_index][args.mapHeader] # Get the 'Rubrik' value from the random index
        st_matches = st_df[st_df[args.mapHeader] == rubrik_value] # Filter ST DataFrame based on the 'Rubrik' value
        print("st_matches: ",st_matches)
        
        # Print current status
        print(f"Trying index {random_index}. Current counts - Without Match: {count_without_match}, Double ST: {count_double_st}, Selected: {len(selected_indices)}")

        # Handling cases where for requirements with  no test case or test case with empty description, i.e not tested
        if st_matches.empty or st_matches['Beskrivning'].isnull().any():
            if count_without_match < required_without_match:
                count_without_match += 1
                selected_indices.add(random_index)
                print(f"Added due to no match, required({required_without_match}) -> total: {count_without_match}.")
        
        if len(st_matches) >= min_st_per_req:
            for st in st_matches:
                if st['Beskrivning'].isnull().any():
                    continue
                
            if count_double_st < one_to_many_tests:
                count_double_st += 1
                double_st_indices.add(random_index)
                print(f"Added due to multiple STs (total {count_double_st}).")
                selected_indices.add(random_index)
                print(f"Added index {random_index}.")


    selected_req_df = req_df.iloc[sorted(list(selected_indices))]
    req_IDdesc = selected_req_df[args.mapHeader].unique()
    filtered_st_df = st_df[st_df[args.mapHeader].isin(req_IDdesc)]

    return selected_req_df, filtered_st_df

###################################################################
# CSV File Processing
###################################################################
req_df = pd.read_csv(req_amina)
st_df = pd.read_csv(st_amina)
#Extrcting requirements and test cases
num_to_extract = int(args.count)  # Number of requirements to extract
req_df, st_df = random_selection_and_filter(num_to_extract, req_df, st_df, args.without_test,args.one_to_many_test)


#Save Extracted RE to a csv file
req_file = f'{directory_path}{args.req_name}_extracted_{num_to_extract}.csv'
req_df.to_csv(req_file, index=False)
print("Saved extracted RE to a csv file")

#req_IDdesc = req_df['Rubrik'].unique()
#st_df = st_df[st_df['Rubrik'].isin(req_IDdesc)]

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



