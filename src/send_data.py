import datetime
import os
import json
import argparse

from dotenv import load_dotenv

from .core.rest import RESTSpecification


parser = argparse.ArgumentParser(description="Process file information.")
parser.add_argument("--sessionName", "-s", dest="session",type=str, default= "MistralAI-REST-at-BTHS-eval", help="Customize the session name")
parser.add_argument("--model", "-m", dest="model",type=bool, default= "mistral", help="Set the model to use")


args = parser.parse_args()

def main() -> None:
    load_dotenv()
    session_name = args.session
    model = args.model
    model.lower()
    print(model) 
    if model == "mixtral":
        model_path = os.getenv("MODEL_PATH")
        token = int(os.getenv("TOKEN_LIMIT"))
        print(f"Using Mixtral model. Session name: {session_name}")
    else: 
        model_path = os.getenv("MODEL_PATH_MIS")
        token = int(os.getenv("TOKEN_LIMIT_MIS"))
        print(f"Using Mistral model. Session name: {session_name}")


    # Load the REST specifications
    specs: RESTSpecification = RESTSpecification.load_specs(
        os.getenv("REQ_PATH"),
        os.getenv("TEST_PATH")
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
