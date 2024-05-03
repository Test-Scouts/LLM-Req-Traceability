import datetime
import os
import json
import argparse

from dotenv import load_dotenv

from .core.rest import GPTResponse, RESTSpecification


def main() -> None:
    parser = argparse.ArgumentParser(description="Process file information using OpenAI's API.")
    parser.add_argument("--sessionName", "-s", dest="session", type=str, default="GPT-3.5-REST-at-BTHS-eval", help="Customize the session name")
    parser.add_argument("--model", "-m", dest="model", type=str, default="gpt3.5", help="Set the model to use. Choose between GPT-3.5 and GPT-4. Default is GPT-3.5.")
    parser.add_argument("--data", "-d", dest="data", type=str, default= "GBG", help="Customize the dataset, not case sensitive. Use MIX for the mix dataset, Mix-small for mix-small-dataset, BTHS for the BTHS dataset, and GBG for the GBG dataset. Default is GBG.")
    parser.add_argument("--system", "-S", dest="system", type=str, default=None, help="Customize the system prompt used. Falls back on a default if not provided.")
    parser.add_argument("--prompt", "-p", dest="prompt", type=str, default=None, help="Customize the prompt used. Include `{req}` in place of the requirement and `{tests}` in place of the tests. Falls back on a default if not provided.")

    args = parser.parse_args()

    load_dotenv()

    session_name = args.session
    model: str = args.model.lower()
    data: str = args.data.lower()
    system_prompt: str = args.system
    prompt: str = args.prompt

    if model == "gpt4":
        model = "gpt-4-turbo-2024-04-09"
        print(f"Using Mistral model. Session name: {session_name}")
    else:
        model = "gpt-3.5-turbo-0125"
        print(f"Using {model}. Session name: {session_name}")

    req_path: str
    test_path: str
    mapping_path: str
    
    if data == "mix":
        print("Info - Using MIX data")
        req_path = os.getenv("MIX_REQ_PATH")
        test_path = os.getenv("MIX_TEST_PATH")
        mapping_path = os.getenv("MIX_MAP_PATH")
    elif args.data.lower() == "mix-small":
        print("Using MIX-small data")
        req_path = os.getenv("S_MIX_REQ_PATH")
        test_path = os.getenv("S_MIX_TEST_PATH")
        mapping_path = os.getenv("S_MIX_MAP_PATH")
    elif args.data.lower() == "bths":
        print("Using BTHS data")
        req_path = os.getenv("BTHS_REQ_PATH")
        test_path = os.getenv("BTHS_TEST_PATH")
        mapping_path = os.getenv("BTHS_MAP_PATH")
    else:
        print("Info - Using GBG data")
        req_path = os.getenv("GBG_REQ_PATH")
        test_path = os.getenv("GBG_TEST_PATH")
        mapping_path = os.getenv("GBG_MAP_PATH")

    # Load the REST specifications
    specs: RESTSpecification = RESTSpecification.load_specs(
        req_path,
        test_path
    )

    # Set system prompt if one was passed
    if system_prompt:
        specs.system_prompt = system_prompt
        print(f"Using the following system prompt:\n{system_prompt}")

    # Set prompt if one was passed
    if prompt:
        specs.prompt = prompt
        print(f"Using the following prompt:\n{prompt}")

    # Send data to local model
    res: GPTResponse = specs.to_gpt(model)

    input_tokens: int = res.input_tokens
    output_tokens: int = res.output_tokens

    payload: dict[str, dict] = {
        "meta": {
            "req_path": req_path,
            "test_path": test_path,
            "mapping_path": mapping_path,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        },
        "data": res.as_dict
    }

    # Log response to a file
    now: datetime.datetime = datetime.datetime.now()
    date: str = str(now.date())
    time: str = str(now.time())

    log_dir: str = f"./out/{session_name}/{date}/{time}"
    os.makedirs(log_dir, exist_ok=True)

    chat_log: str = f"{log_dir}/res.json"
    with open(chat_log, "w") as out:
        json.dump(payload, out, indent=2)

    # Log the token usage
    stats_log: str = f"{log_dir}/stats.log"
    print(f"Logging token usage to {stats_log}")
    with open(stats_log, "w+") as f:
        f.write(f"{input_tokens=}\n{output_tokens=}")


if __name__ == "__main__":
    main()
