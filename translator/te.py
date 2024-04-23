import pandas as pd
import dotenv
import os

dotenv.load_dotenv()
req_amina:str = os.getenv("REQ_AMINA_CSV")
st_amina:str = os.getenv("ST_AMINA_CSV")
req_df = pd.read_csv(req_amina)
h = req_df.columns.tolist()
print(h)



