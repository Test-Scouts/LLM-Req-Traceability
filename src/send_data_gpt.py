import datetime
import os
import json

from dotenv import load_dotenv

from .core.rest import RESTSpecification


def main() -> None:
    load_dotenv()

    # Load the REST specifications
    specs: RESTSpecification = RESTSpecification.load_specs(
        os.getenv("REQ_PATH"),
        os.getenv("TEST_PATH")
    )

    # Send data to local model
    res: dict[str, list[str]]
    data: tuple[int, int]
    
    model: str = "gpt-3.5-turbo-0125"
    res, data = specs.to_gpt(
        model
    )

    input_tokens: int
    output_tokens: int

    input_tokens, output_tokens = data

    # Log response to a file
    now: datetime.datetime = datetime.datetime.now()
    date: str = str(now.date())
    time: str = str(now.time())

    log_dir: str = f"./out/{model}/{date}/{time}"
    os.makedirs(log_dir, exist_ok=True)

    chat_log: str = f"{log_dir}/res.json"
    with open(chat_log, "w") as out:
        json.dump(res, out, indent=2)

    # Log the token usage
    stats_log: str = f"{log_dir}/stats.log"
    print(f"Logging token usage to {stats_log}")
    with open(stats_log, "w+") as f:
        f.write(f"{input_tokens=}\n{output_tokens=}")


if __name__ == "__main__":
    main()
