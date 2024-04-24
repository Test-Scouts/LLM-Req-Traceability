import torch
from transformers import pipeline, StoppingCriteriaList, StoppingCriteria
import dotenv
import os
import pandas as pd

dotenv.load_dotenv()

device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = os.getenv("AI_SWE-MODEL_PATH")

#Load the environment variables
req_amina:str = os.getenv("E_REQ")
st_amina:str = os.getenv("E_ST")

#Load the AMINA requirements and test cases
req_df = pd.read_csv(req_amina)
st_df = pd.read_csv(st_amina)

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



###################################################################
# Translation process
###################################################################
# Iterate over each cell in the DataFrame and update it
def process_value(df):
    for column in df.columns:
        if column == 'ID' or column == 'GE_KravID':
            continue
        for index in df.index:
            original_value = df.at[index, column]
            new_value = translate_to_swedish(original_value)
            df.at[index, column] = new_value
    return df


###################################################################
# Saving traslated version to a csv file
###################################################################
directory_path = "../src/GE-data-swe/English/"

# Translate the extracted RE
print("Translating the extracted RE...")
req_df_translated = process_value(req_df)
traslated_req_file = f'{directory_path}AMINA_requirement_translated.csv'
print("Saving the translated RE")
req_df_translated.to_csv(traslated_req_file, index=False)

# Translate the extracted ST
print("Translating the extracted ST...")
st_df_translated = process_value(st_df)
traslated_st_file = f'{directory_path}AMINA_testcases_translated.csv'
print("Saving the translated ST")
st_df_translated.to_csv(traslated_st_file, index=False)
