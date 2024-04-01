import csv
import datetime
import os
import json

from dotenv import load_dotenv
from .util.model import Session
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
        # Remove the headers (0th row)
        test_list: list[dict[str, str]] = list(map(lambda row: {k: row[k] for k in row.keys() if k in fields}, reader))

    # Set up a session
    model_path: str = os.getenv("MODEL_PATH")
    max_new_tokens: int = int(os.getenv("TOKEN_LIMIT"))
    session_name: str = "MistralAI-REST-at-BTHS-eval"
    session: Session = Session.create(
        session_name,
        model_path,
        max_new_tokens,
        "You are a helpful AI assistant."  # Default system prompt of OpenAI
    )

    res: list[str] = []
    for req in req_list:
        res.append(session.prompt(format_req_is_tested_prompt(test_list, req), True))

    now: str = str(datetime.datetime.now()).replace(" ", "-")

    log_dir: str = f"./out/{session_name}/{now}"
    os.makedirs(log_dir, exist_ok=True)

    with open(f"{log_dir}/chat.txt", "w+") as out:
        out.write("\n".join(res))


if __name__ == "__main__":
    main()
