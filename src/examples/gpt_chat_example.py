import json
import datetime
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion


def main() -> None:
    # Requires OPENAI_API_KEY and OPENAI_BASE_URL
    load_dotenv()

    # Chat with an intelligent assistant in your terminal
    client: OpenAI = OpenAI()

    history: list[dict[str, str]] = []

    prompt: str = input("> ")
    history.append({"role": "user", "content": prompt})

    in_tokens: int = 0
    out_tokens: int = 0

    model: str = "gpt-3.5-turbo-0125"
    # Use Literal["end"] as chat terminator
    while prompt != "end":
        completion: ChatCompletion = client.chat.completions.create(
            model=model,
            messages=history,
            temperature=0.1
        )

        # Get response message
        new_message: dict[str, str] = {"role": "assistant", "content": completion.choices[0].message.content}
        print(f"GPT> {new_message['content']}")
        history.append(new_message)

        # Update token usage
        in_tokens += completion.usage.prompt_tokens
        out_tokens += completion.usage.completion_tokens

        # Input new prompt
        prompt = input("> ")
        history.append({"role": "user", "content": prompt})

    now: str = str(datetime.datetime.now()).replace(" ", "-")

    log_dir: str = f"./out/{model}/{now}"
    os.makedirs(log_dir, exist_ok=True)

    # Log the chat
    chat_log: str = f"{log_dir}/chat.json"
    print(f"Logging chat to {chat_log}")
    with open(chat_log, "w+") as f:
        json.dump(history, f, indent=2)

    # Log the token usage
    stats_log: str = f"{log_dir}/stats.log"
    print(f"Logging token usage to {stats_log}")
    with open(stats_log, "w+") as f:
        f.write(f"{in_tokens=}\n{out_tokens=}")

    print("Done!")


if __name__ == "__main__":
    main()
