import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
from dotenv import load_env
from typing import Final


SYSTEM_PROMPT: Final[str] = "You are a helpful AI called Kalle."


def gen_prompt(user_prompt: str) -> str:
    return f"[SYS] {SYSTEM_PROMPT} [\\SYS]\n\n{user_prompt}"


def main() -> None:
    load_env()


    model_id = os.getenv("MODEL_PATH")

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")

    user_prompt = gen_prompt("Who are you? and what can you help me with?")

    messages = [
        {"role": "user", "content": user_prompt}
    ]

    input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt").to("cuda")

    outputs = model.generate(
        input_ids,
        max_new_tokens=4096,
        do_sample=True,
        temperature=0.7
    )
    print(tokenizer.decode(outputs[0], skip_special_tokens=True))


if __name__ == "__main__":
    main()
