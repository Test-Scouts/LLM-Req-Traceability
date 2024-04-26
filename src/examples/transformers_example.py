import os
from dotenv import load_dotenv

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BatchEncoding,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    PreTrainedModel
)
import torch


def main() -> None:
    load_dotenv()

    # Model data
    model_id: str = os.getenv("MODEL_PATH")
    max_new_tokens: int = int(os.getenv("TOKEN_LIMIT"))

    # Load model# Load the model and its tokenizer
    tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast = AutoTokenizer.from_pretrained(model_id)

    model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    model.eval()

    # Create an empty message history
    messages: list[dict[str, str]] = []

    user_prompt = input("> ")
    messages.append({"role": "user", "content": user_prompt})

    input_ids: str | list[str] = tokenizer.apply_chat_template(messages, return_tensors="pt")

    outputs = model.generate(
        input_ids,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.1
    )
    res = tokenizer.decode(outputs[0])
    print(f"\nLLM> {res}\n")


if __name__ == "__main__":
    main()
