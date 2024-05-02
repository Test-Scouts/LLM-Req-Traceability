import json


def format_req_is_tested_prompt(tests: list[dict[str, str]], req: dict[str, str]) -> str:
    return "I have this requirement:" \
        + "\n\n" \
        + json.dumps(req) \
        + "\n\n" \
        + 'Would you say that any of the test cases in the file "tests.csv" are testing the requirement? If yes, answer ONLY with the test case ID(s) that are testing the requirement in the following form:' \
        + "\n\n" \
        + '{"requirementID": "<insert requirement id>", "tests": "<insert test id 1>, <insert test id 2>, <insert test id 3>, ..."}' \
        + "\n\n" \
        + "DO NOT ADD ANY TEXT BEFORE OR AFTER THE CURLY BRACKETS. If no, answer ONLY in the following form:" \
        + "\n\n" \
        + '{"requirementID": "<insert requirement id>", "tests": ""}' \
        + "\n\n" \
        + 'The contents of "tests.csv" are:' \
        + "\n\n" \
        + "\n".join([json.dumps(test) for test in tests]) \
        + "\n\n" \
        + "I am going to parse your input in my javascript program, therefore, ONLY ANSWER IN THE FORM I GAVE YOU."
