import os
import dotenv
import pandas as pd

dotenv.load_dotenv()
#Load the environment variables
req_amina:str = os.getenv("E_REQ")
st_amina:str = os.getenv("E_ST")

print("REQ Path:", req_amina)
print("ST Path:", st_amina)

#Load the AMINA requirements and test cases
req_df = pd.read_csv(req_amina)
st_df = pd.read_csv(st_amina)

print(req_df.head())
