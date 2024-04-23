import random
import dotenv
import os
import argparse
import pandas as pd
import torch
import sys
import helper

dotenv.load_dotenv()

# Set the device to use the GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
# Load the path to the model from the environment variables
#model_path = os.getenv("AI_SWE-MODEL_PATH")

#flag - provide the number of requests to extract
#flag - the mapping header 

parser = argparse.ArgumentParser(description="Process file information.")
#Add arguments
parser.add_argument("--count", "-c", dest="count",type=int, default= 2, help="Number of extractions")
parser.add_argument("--re-not-test", "-rnt", dest="without_test",type=int, default= 1, help="Number of requirements without test cases")
parser.add_argument("--one_re_to_many_test", "-otm", dest="one_to_many_test",type=int, default= 0, help="Number of requirements with at least two test cases")
parser.add_argument("--dir", "-d", dest="directory",type=str, help="Directory to store the extracted files")
parser.add_argument("--map", "-m", dest="mapHeader",type=str,default='GE_KravID', help="Mapping header for the extracted of test")
parser.add_argument("--test-name", "-tn", dest="st_name",type=str, default="ST", help="Name of the extracted test cases file")
parser.add_argument("--req-name", "-rn", dest="req_name",type=str, default="RE", help="Name of the extracted requirements file")
parser.add_argument("--amina_info", "-ai", dest="amina_info",type=bool ,default=False,help="Get information about the AMINA requirements and test cases")
parser.add_argument("--amina_detailed_info", "-aid", dest="amina_detailed_info",type=bool ,default=False,help="Get detailed information about the AMINA requirements and test cases")

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

#Load the AMINA requirements and test cases
req_df = pd.read_csv(req_amina)
st_df = pd.read_csv(st_amina)

#Get information about the AMINA requirements and test cases
if args.amina_info:
    helper.print_info_AMINA_requirements_and_tests(req_df, st_df, detailed=False)
    sys.exit(0)
if args.amina_detailed_info:
    helper.print_info_AMINA_requirements_and_tests(req_df, st_df, detailed=True)
    sys.exit(0)

###################################################################
# Random selection and filtering
# This only concider the ST that are connected to the RE
# they are constraint to the RE that have been visited
###################################################################
def random_selection_and_filter(num_to_select: int, req_df: pd.DataFrame, st_df: pd.DataFrame, 
                                required_without_match: int, one_to_many_tests: int):
    if num_to_select > len(req_df):
        raise ValueError("Number of unique values to select exceeds the range of values.")
    
    selected_req = set()
    count_without_match = 0
    count_double_st = 0
    count_select_without_restriction = 0
    select_without_restriction = num_to_select - required_without_match - one_to_many_tests
    num_of_visited_req = set() 

    # Track indices that fulfill the multiple ST requirement
    one_to_many_indices = set()
    # To store the test cases IDs that are selected
    selected_st = set()
    # Requirement that are not tested
    re_not_tested = set()
 
    while len(selected_req) < (count_select_without_restriction + required_without_match + one_to_many_tests):
        if len(num_of_visited_req) == len(req_df):
            print(f"""All requirements have been visited. 
                  Information:
                  Total: {len(num_of_visited_req)}
                  Nr of requiremts with multiple test cases are (1 to Many): {len(one_to_many_indices)} (where at least 2 test steps are not empty)
                  Nr of requiremnts that are not tested: {len(re_not_tested)}
                """)
            sys.exit(1)

        # Randomly select an index
        random_index = random.randint(0, len(req_df) - 1)

        # Check if the index has already been visited
        if(random_index in num_of_visited_req):
            #print(f"Index {random_index} has already been visited.")
            continue
        
        num_of_visited_req.add(random_index) # Add the index to the visited set
        RE_ID_header = args.mapHeader
        RE_ID_value = req_df.iloc[random_index][RE_ID_header] # Get the RE_ID value from the random index
        st_matches = st_df[st_df[RE_ID_header] == RE_ID_value] # Filter ST DataFrame based on the 'Rubrik' value

        #print(f"Trying index {random_index}. Current counts - Without Match(not tested): {count_without_match}, 1-M-ST: {count_double_st}, Selected: {len(selected_req)}")
    
        # Handling cases where for requirements with  no test case or test case with empty description, i.e not tested
        if len(st_matches) == 0 or st_matches['Beskrivning'].isnull().all(): #No test case found for the requirement
            re_not_tested.add(random_index) # Add the index to the not tested set
            #for e in re_not_tested:
            #    print("Not tested:",st_df.iloc[e][RE_ID_header])
            #print("\n\n")

            if count_without_match < required_without_match:
                count_without_match += 1
                selected_req.add(random_index)
                if not st_matches.empty:
                    selected_st.update(st_matches['ID'])
                    print(f" Current counts(wanted:{num_to_select}) - Without Match(not tested): {count_without_match}, 1-M-ST: {count_double_st}, Selected: {len(selected_req)}")
                
        else:

            if len(st_matches) > 1 and len(one_to_many_indices) < one_to_many_tests: # Check if the requirement has at least 2 test cases  
                if count_double_st < one_to_many_tests:
                    count_double_st += 1
                    one_to_many_indices.add(random_index)
                    selected_req.add(random_index)
                    #Store the test cases in st_matches
                    selected_st.update(st_matches['ID'])
                    print(f" Current counts - Without Match(not tested): {count_without_match}, 1-M-ST: {count_double_st}, Selected: {len(selected_req)}")


            elif len(selected_req) < select_without_restriction and len(st_matches) > 0:
                count_select_without_restriction += 1
                selected_req.add(random_index)
                #Store the test cases in st_matches
                selected_st.update(st_matches['ID'])
                print(f"Current counts - Without Match(not tested): {count_without_match}, 1-M-ST: {count_double_st}, Selected: {len(selected_req)}")


    # Extract rows from req_df and st_df based on the IDs
    selected_req_df = req_df.iloc[sorted(list(selected_req))]
    selected_st_df = st_df[st_df['ID'].isin(selected_st)]

    print(selected_req_df)
    print("\n\n")
    print(selected_st_df)

    return selected_req_df, selected_st_df

###################################################################
# AI Sweden Model Setup
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


###################################################################
# CSV File Processing
###################################################################

#Extracting requirements and test cases
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



