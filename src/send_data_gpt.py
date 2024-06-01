"""
Script for running REST-at using an OpenAI GPT model specified through the command line.
System prompt and user prompt are also specified through the command line.
The dataset and session name to use are also specified through the command line.

Requires the following envs to work:
```python
# Paths to local models
MODEL_PATH: Path
MODEL_PATH_MIX22: Path
MODEL_PATH_LLAMA: Path
MODEL_PATH_MIS: Path

# max_new_tokens variables for models
TOKEN_LIMIT: int
TOKEN_LIMIT_MIX22: int
TOKEN_LIMIT_LLAMA: int
TOKEN_LIMIT_MIS: int

# Data paths to REST spec files
MIX_REQ_PATH: Path
S_MIX_REQ_PATH: Path
BTHS_REQ_PATH: Path
GBG_REQ_PATH: Path
MIX_TEST_PATH: Path
S_MIX_TEST_PATH: Path
BTHS_TEST_PATH: Path
GBG_TEST_PATH: Path
MIX_MAP_PATH: Path
S_MIX_MAP_PATH: Path
BTHS_MAP_PATH: Path
GBG_MAP_PATH: Path
```

Copyright:
----------
(c) 2024 Test-Scouts

License:
--------
MIT (see LICENSE for more information)
"""
import datetime
import os
import json
import argparse
import traceback

from dotenv import load_dotenv

from .core.rest import GPTResponse, RESTSpecification


def main() -> None:
    parser = argparse.ArgumentParser(description="Process file information using OpenAI's API.")
    parser.add_argument("--sessionName", "-s", dest="session", type=str, default="GPT-3.5-REST-at-BTHS-eval", help="Customize the session name")
    parser.add_argument("--model", "-m", dest="model", type=str, default="gpt-3.5", help="Set the model to use. Choose between GPT-3.5 and GPT-4. Default is GPT-3.5.")
    parser.add_argument("--data", "-d", dest="data", type=str, default= "GBG", help="Customize the dataset, not case sensitive. Use MIX for the mix dataset, Mix-small for mix-small-dataset, BTHS for the BTHS dataset, and GBG for the GBG dataset. Default is GBG.")
    parser.add_argument("--system", "-S", dest="system", type=str, default=None, help="Path to the system prompt used. Falls back on a default if not provided.")
    parser.add_argument("--prompt", "-p", dest="prompt", type=str, default=None, help="Path to the prompt used. Include `{req}` in place of the requirement and `{tests}` in place of the tests. Falls back on a default if not provided.")

    args = parser.parse_args()

    load_dotenv()

    session_name = args.session
    model: str = args.model.lower()
    data: str = args.data.lower()
    system_prompt_path: str = args.system
    prompt_path: str = args.prompt

    if model == "gpt-4":
        model = "gpt-4-turbo-2024-04-09"
    else:
        model = "gpt-3.5-turbo-0125"

    print(f"Info - Using {model}. Session name: {session_name}")

    req_path: str
    test_path: str
    mapping_path: str
    
    if data == "mix":
        print("Info - Using MIX data")
        req_path = os.getenv("MIX_REQ_PATH")
        test_path = os.getenv("MIX_TEST_PATH")
        mapping_path = os.getenv("MIX_MAP_PATH")
    elif args.data.lower() == "mix-small":
        print("Info - Using MIX-small data")
        req_path = os.getenv("S_MIX_REQ_PATH")
        test_path = os.getenv("S_MIX_TEST_PATH")
        mapping_path = os.getenv("S_MIX_MAP_PATH")
    elif args.data.lower() == "bths":
        print("Info - Using BTHS data")
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
    if system_prompt_path:
        try:
            system_prompt: str
            # Read the prompt from the specified file
            with open(system_prompt_path) as f:
                system_prompt = f.read()

            # Set the system prompt
            specs.system_prompt = system_prompt
            print(f"Using the following system prompt:\n{system_prompt}")
        except Exception:
            print(f"Error loading system prompt from {system_prompt_path}")
            traceback.print_exc()
    # Otherwise, use the default system prompt
    else:
        try:
            system_prompt: str
            # Read the prompt from the default file
            with open("./prompts/system/default.txt") as f:
                system_prompt = f.read()

            # Set the system prompt
            specs.system_prompt = system_prompt
            print(f"Using the default system prompt:\n{system_prompt}")
        except Exception:
            print(f"Error loading default system prompt")
            traceback.print_exc()

    # Set prompt if one was passed
    if prompt_path:
        try:
            prompt: str
            # Read the prompt from the specified file
            with open(prompt_path) as f:
                prompt = f.read()

            # Set the prompt
            specs.prompt = prompt
            print(f"Using the following prompt:\n{prompt}")
        except Exception:
            print(f"Error loading prompt")
            traceback.print_exc()
    # Otherwise, use the default prompt
    else:
        try:
            prompt: str
            # Read the prompt from the default file
            with open("./prompts/user/default.txt") as f:
                prompt = f.read()

            # Set the prompt
            specs.prompt = prompt
            print(f"Using the default prompt:\n{prompt}")
        except Exception:
            print(f"Error loading default prompt")
            traceback.print_exc()

    # Send data to local model
    res: GPTResponse = specs.to_gpt(model)

    input_tokens: int = res.input_tokens
    output_tokens: int = res.output_tokens
    fingerprint: str = res.fingerprint

    payload: dict[str, dict] = {
        "meta": {
            "req_path": req_path,
            "test_path": test_path,
            "mapping_path": mapping_path,
            "fingerprint": fingerprint,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        },
        "data": res.as_dict,
        "raw": res.raw_res
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
