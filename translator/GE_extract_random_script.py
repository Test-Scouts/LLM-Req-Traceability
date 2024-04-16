import random
import csv
import dotenv
import os
import pandas as pd
dotenv.load_dotenv()

#flag - provide the number of requests to extract
#flag - the mapping header 


max_req:int = int(os.getenv("END_REQ"))
num_of_req:int = int(os.getenv("NUM_OF_REQ"))

req_amina:str = os.getenv("REQ_AMINA_CSV")
st_amina:str = os.getenv("ST_AMINA_CSV")

def random_selection_unique_values(num_to_select:int ,max_row_in_csv:int):
    if num_to_select > max_row_in_csv + 1: 
        raise ValueError("Number of unique values to select exceeds the range of values.")
    
    random_list = set()
    while len(random_list) < num_to_select:
        random_list.add(random.randint(0, max_row_in_csv-2))
    sorted_list = sorted(list(random_list))
    return sorted_list


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