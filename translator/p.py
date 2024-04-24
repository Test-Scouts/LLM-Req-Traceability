import pandas as pd
import dotenv
import os
import numpy as np
dotenv.load_dotenv()

#Load the environment variables
req_amina:str = os.getenv("REQ_AMINA_CSV")
st_amina:str = os.getenv("ST_AMINA_CSV")

#Load the AMINA requirements and test cases
req_df = pd.read_csv(req_amina)
st_df = pd.read_csv(st_amina)

############################################
# Calculate not tested requirements
############################################

# Filter where 'Beskrivning' is empty
empty_besk = st_df[st_df['Beskrivning'].isnull() | (st_df['Beskrivning'] == '')]


# Find all unique GE_KravID in st_df
tested_ids = st_df['GE_KravID'].unique()

# Filter out rows in req_df where GE_KravID is not in tested_ids
untested_reqs = req_df[~req_df['GE_KravID'].isin(tested_ids)]

# Step 2: Include requirements with empty descriptions
# Append requirements where 'Beskrivning' is empty to the list of untested requirements
empty_description_reqs = req_df[req_df['Beskrivning'].isnull() | (req_df['Beskrivning'] == '')]

# Combine both sets of untested requirements without duplicates
#final_untested_reqs = pd.concat([untested_reqs, empty_description_reqs]).drop_duplicates()


    # Find requirements that have not been tested
untested_requirements = req_df[~req_df['ID'].isin(st_df['GE_KravID'])]

# If 'Beskrivning' column is empty, consider it as untested requirement
untested_requirements = untested_requirements[untested_requirements['Beskrivning'].isnull() | (untested_requirements['Beskrivning'] == '')]



# Assuming st_df and req_df are already loaded, for example:
# st_df = pd.read_csv('path_to_st_df.csv')
# req_df = pd.read_csv('path_to_req_df.csv')

# Find GE_KravID in st_df that are not in req_df
non_existing_ge_kravid = st_df[~st_df['GE_KravID'].isin(req_df['GE_KravID'])]['GE_KravID']

# Print the result
print("GE_KravID in 'st_df' that do not exist in 'req_df':")
print(non_existing_ge_kravid)
