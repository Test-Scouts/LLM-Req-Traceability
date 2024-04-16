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
text = "Jag har krav att översätta till Engelska som är för ett projekt"

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

print(response[0]["generated_text"].split("<s>Bot: ")[-1])
