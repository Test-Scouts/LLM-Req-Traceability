import os
from dotenv import load_dotenv
from ..util import model as ml


def main() -> None:
    load_dotenv()

    model_id: str = os.getenv("MODEL_PATH")
    max_new_tokens: int = 4096

    model : ml.Model = ml.Model.load(model_id, max_new_tokens)

    messages: list[dict[str, str]] = []

    while True:
        user_prompt = input("> ")
        res = model.prompt(messages, user_prompt)
        print(f"\nLLM> {res}\n")


if __name__ == "__main__":
    main()
