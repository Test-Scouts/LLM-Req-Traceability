import csv
import datetime
import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion

from .util.prompt import format_req_is_tested_prompt


def main() -> None:
    load_dotenv()

    # Load requirements file and filter the desired fields
    req_list: list[dict[str, str]]
    with open(os.getenv("REQ_PATH")) as reqs:
        fields: list[str] = [
            "ID",
            "Feature",
            "Description"
        ]
        reader: csv.DictReader = csv.DictReader(reqs)

        req_list: list[dict[str, str]] = list(map(lambda row: {k: row[k] for k in row.keys() if k in fields}, reader))


    # Load requirements file and filter the desired fields
    test_list: list[dict[str, str]]
    with open(os.getenv("TEST_PATH")) as tests:
        fields: list[str] = [
            "ID",
            "Purpose",
            "Test steps"
        ]
        reader: csv.DictReader = csv.DictReader(tests)

        test_list: list[dict[str, str]] = list(map(lambda row: {k: row[k] for k in row.keys() if k in fields}, reader))

    # Set up a session
    model: str = "gpt-3.5-turbo-0125"
    client: OpenAI = OpenAI()

    input_tokens: int = 0
    output_tokens: int = 0
    history: list[dict[str, str]]
    res: list[str] = []
    for req in req_list:
        history = [{"role": "user", "content": format_req_is_tested_prompt(test_list, req)}]
        completion: ChatCompletion = client.chat.completions.create(
            model=model,
            messages=history,
            temperature=0.1
        )

        res.append(completion.choices[0].message.content)

        input_tokens += completion.usage.prompt_tokens
        output_tokens += completion.usage.completion_tokens

    now: str = str(datetime.datetime.now()).replace(" ", "-")

    log_dir: str = f"./out/{model}/{now}"
    os.makedirs(log_dir, exist_ok=True)

    chat_log: str = f"{log_dir}/chat.txt"
    with open(chat_log, "w") as out:
        out.write("\n".join(res))

    # Log the token usage
    stats_log: str = f"{log_dir}/stats.log"
    print(f"Logging token usage to {stats_log}")
    with open(stats_log, "w+") as f:
        f.write(f"{input_tokens=}\n{output_tokens=}")


if __name__ == "__main__":
    main()
