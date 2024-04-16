import torch
from transformers import pipeline, StoppingCriteriaList, StoppingCriteria
import dotenv
import os

dotenv.load_dotenv()

device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = os.getenv("AI_SWE-MODEL_PATH")

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



requirement = """
S257 - Ny nyckel/lösnenord

Fabriksinställningar och leverantörsspecifika standardlösenord eller krypteringsnycklar ska (S257) ersättas 
med nyskapade motsvarigheter som uppfyller Beställarens krav.
"""
test_case = """
S257 - Ny nyckel/lösenord

Exporta nyckel för mätaren från KMS.
Koppla upp mot mätaren med den exporterade nyckeln med MeterTool.
Byt nyckel för mätaren i KMS.
Exportera nycklar för mätaren igen från KMS.
Koppla upp mot mätaren med MeterTool igen med de gamla kryptonycklarna.
Importera nya nycklarna i MeterTool.
Koppla upp mot mätaren med MeterTool igen med de nya kryptonycklarna.

"""

sp="\n\n"

print(translate_to_swedish(requirement))
print(sp)
print(translate_to_swedish(test_case))
