import csv
import datetime
import os
import json

from dotenv import load_dotenv
from util.model import Session
from util.prompt import format_req_is_tested_prompt


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
        # Remove the headers (0th row)
        req_list = list(map(lambda row: {k: row[k] for k in row.keys() if k in fields}, reader))[1::]


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
        test_list = list(map(lambda row: {k: row[k] for k in row.keys() if k in fields}, reader))[1::]

    # Set up a session
    model_path: str = os.getenv("MODEL_PATH")
    max_new_tokens: int = int(os.getenv("TOKEN_LIMIT"))
    session_name: str = f"{model_path}-REST-at-BTHS-eval"
    session: Session = Session.create(
        session_name,
        model_path,
        max_new_tokens,
        "You are a helpful AI assistant."  # Default system prompt of OpenAI
    )

    for req in req_list:
        session.prompt(format_req_is_tested_prompt(test_list, req))

    # Filter message history for responses
    # Should be JSON strings
    res: list[str] = filter(lambda msg: msg["role"] == "assistant", session.get_history())

    with open(f"{session_name}-{datetime.datetime.now()}.json", "w") as out:
        json.dump(res, out, indent=2)


if __name__ == "__main__":
    main()