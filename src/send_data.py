import datetime
import os
import json
import argparse

from dotenv import load_dotenv

from .core.rest import RESTSpecification


parser = argparse.ArgumentParser(description="Process file information.")
parser.add_argument("--sessionName", "-s", dest="session",type=str, default= "MistralAI-REST-at-BTHS-eval", help="Customize the session name")
parser.add_argument("--model", "-m", dest="model",type=str, default= "mistral", help="Set the model to use")
parser.add_argument("--data", "-d", dest="data",type=str, default= "GBG", help="Customize the dataset, not case sensitive. Use mix for the mix-dataset, mix-small for the small mix-dataset, bths for the BTHS-dataset, and GBG for the GBG-dataset. Default is GBG.")


args = parser.parse_args()

def main() -> None:
    load_dotenv()
    session_name = args.session
    model = args.model

    if model.lower() == "mixtral":
        model_path = os.getenv("MODEL_PATH")
        token = int(os.getenv("TOKEN_LIMIT"))
        print(f"Using Mixtral model. Session name: {session_name}")
    else: 
        model_path = os.getenv("MODEL_PATH_MIS")
        token = int(os.getenv("TOKEN_LIMIT_MIS"))
        print(f"Using Mistral model. Session name: {session_name}")

    if args.data.lower() == "mix":
        print("Using MIX data")
        req_path = os.getenv("MIX_REQ_PATH")
        test_path = os.getenv("MIX_TEST_PATH")
    elif args.data.lower() == "mix-small":
        print("Using MIX data")
        req_path = os.getenv("S_MIX_REQ_PATH")
        test_path = os.getenv("S_MIX_TEST_PATH")
    elif args.data.lower() == "bths":
        print("Using BTHS data")
        req_path = os.getenv("BTHS_REQ_PATH")
        test_path = os.getenv("BTHS_TEST_PATH")
    else:
        print("Using GBG data")
        req_path = os.getenv("GBG_REQ_PATH")
        test_path = os.getenv("GBG_TEST_PATH")
        
    print(f"Model path: {model_path}")
    print(f"Token limit: {token}")
    print(f"Request path: {req_path}")
    print(f"Test path: {test_path}")

    # Load the REST specifications
    specs: RESTSpecification = RESTSpecification.load_specs(
        req_path,
        test_path
    )

    # Send data to local model
    res: dict[str, list[str]] = specs.to_local(
        model_path,token
    )

    # Log response to a file
    now: datetime.datetime = datetime.datetime.now()
    date: str = str(now.date())
    time: str = str(now.time())

    log_dir: str = f"./out/{session_name}/{date}/{time}"
    os.makedirs(log_dir, exist_ok=True)

    with open(f"{log_dir}/res.json", "w+") as out:
        json.dump(res, out, indent=2)


if __name__ == "__main__":
    main()
