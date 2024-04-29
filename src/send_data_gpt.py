import datetime
import os
import json
import argparse

from dotenv import load_dotenv

from .core.rest import RESTSpecification



def main() -> None:
    parser = argparse.ArgumentParser(description="Process file information.")
    parser.add_argument("--sessionName", "-s", dest="session", type=str, default="GPT-3.5-REST-at-BTHS-eval", help="Customize the session name")
    parser.add_argument("--model", "-m", dest="model", type=str, default="gpt3.5", help="Set the model to use. Choose between GPT-3.5 and GPT-4. Default is GPT-3.5.")
    parser.add_argument("--data", "-d", dest="data", type=str, default="GBG", help="Customize the dataset, not case sensitive. Use MIX for the mix dataset, BTHS for the BTHS dataset, and GBG for the GBG dataset. Default is GBG.")

    args = parser.parse_args()

    load_dotenv()

    session_name = args.session
    model: str = args.model.lower()
    data: str = args.data.lower()

    if model == "gpt4":
        model = "gpt-4-turbo-2024-04-09"
        print(f"Using Mistral model. Session name: {session_name}")
    else:
        model = "gpt-3.5-turbo-0125"
        print(f"Using {model}. Session name: {session_name}")

    req_path: str
    test_path: str
    
    if data == "mix":
        print("Using MIX data")
        req_path = os.getenv("MIX_REQ_PATH"),
        test_path = os.getenv("MIX_TEST_PATH")
    elif data == "bths":
        print("Using BTHS data")
        req_path = os.getenv("BTHS_REQ_PATH"),
        test_path = os.getenv("BTHS_TEST_PATH")
    else:
        print("Using GBG data")
        req_path = os.getenv("GBG_REQ_PATH"),
        test_path = os.getenv("GBG_TEST_PATH")

    # Load the REST specifications
    specs: RESTSpecification = RESTSpecification.load_specs(
        req_path,
        test_path
    )

    # Send data to local model
    res: dict[str, list[str]]
    data: tuple[int, int]
    

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
