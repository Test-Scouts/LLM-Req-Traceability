import datetime
import os
import json

from dotenv import load_dotenv

from core.rest import RESTSpecification


def main() -> None:
    load_dotenv()

    # Load the REST specifications
    specs: RESTSpecification = RESTSpecification.load_specs(
        os.getenv("REQ_PATH"),
        os.getenv("TEST_PATH")
    )

    # Send data to local model
    res: dict[str, list[str]] = specs.to_local(
        os.getenv("MODEL_PATH"),
        int(os.getenv("TOKEN_LIMIT"))
    )

    # Log response to a file
    session_name: str = "MistralAI-REST-at-BTHS-eval"
    now: datetime.datetime = datetime.datetime.now()
    date: str = str(now.date())
    time: str = str(now.time())

    log_dir: str = f"./out/{session_name}/{date}/{time}"
    os.makedirs(log_dir, exist_ok=True)

    with open(f"{log_dir}/res.json", "w+") as out:
        json.dump(res, out, indent=2)


if __name__ == "__main__":
    main()
