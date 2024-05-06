import datetime
import os
import json
import argparse
import traceback

from dotenv import load_dotenv

from .core.rest import RESTSpecification, Response


def main() -> None:
    parser = argparse.ArgumentParser(description="Process file information.")
    parser.add_argument("--sessionName", "-s", dest="session", type=str, default="MistralAI-REST-at-BTHS-eval", help="Customize the session name")
    parser.add_argument("--model", "-m", dest="model", type=str, default="mistral", help="Set the model to use")
    parser.add_argument("--data", "-d", dest="data", type=str, default="GBG", help="Customize the dataset, not case sensitive. Use MIX for the mix dataset, Mix-small for mix-small-dataset, BTHS for the BTHS dataset, and GBG for the GBG dataset. Default is GBG.")
    parser.add_argument("--system", "-S", dest="system", type=str, default=None, help="Path to the system prompt used. Falls back on a default if not provided.")
    parser.add_argument("--prompt", "-p", dest="prompt", type=str, default=None, help="Path to the prompt used. Include `{req}` in place of the requirement and `{tests}` in place of the tests. Falls back on a default if not provided.")

    args = parser.parse_args()

    load_dotenv()
    session_name = args.session
    model: str = args.model.lower()
    data: str = args.data.lower()
    system_prompt_path: str = args.system
    prompt_path: str = args.prompt

    if model == "mixtral":
        model_path = os.getenv("MODEL_PATH")
        token = int(os.getenv("TOKEN_LIMIT"))
        print(f"Using Mixtral model. Session name: {session_name}")
    elif model == "mixtral22":
        model_path = os.getenv("MODEL_PATH_MIX22")
        token = int(os.getenv("TOKEN_LIMIT_MIX22"))
        print(f"Using Mixtral model. Session name: {session_name}")
    elif model == "llama":
        model_path = os.getenv("MODEL_PATH_LLAMA")
        token = int(os.getenv("TOKEN_LIMIT_LLAMA"))
        print(f"Using LLaMA model. Session name: {session_name}")
    else: 
        model_path = os.getenv("MODEL_PATH_MIS")
        token = int(os.getenv("TOKEN_LIMIT_MIS"))
        print(f"Using Mistral model. Session name: {session_name}")

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
        
    print(f"Model path: {model_path}")
    print(f"Token limit: {token}")
    print(f"Requirements path: {req_path}")
    print(f"Tests path: {test_path}")

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
    res: Response = specs.to_local(model_path, token)

    payload: dict[str, dict] = {
        "meta": {
            "req_path": req_path,
            "test_path": test_path,
            "mapping_path": mapping_path
        },
        "data": res.as_dict
    }

    # Log response to a file
    now: datetime.datetime = datetime.datetime.now()
    date: str = str(now.date())
    time: str = str(now.time())

    log_dir: str = f"./out/{session_name}/{date}/{time}"
    os.makedirs(log_dir, exist_ok=True)

    with open(f"{log_dir}/res.json", "w+") as out:
        json.dump(payload, out, indent=2)


if __name__ == "__main__":
    main()
