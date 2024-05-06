import json


_insert_req: str = r"{req}"
_insert_tests: str = r"{tests}"

_default_prompt: str = f"""I have this requirement:

{_insert_req}

Would you say that any of the test cases in the file "tests.json" are testing the requirement? If yes, answer ONLY with the test case ID(s) that are testing the requirement in the following form:

"[<insert test id 1>, <insert test id 2>, <insert test id 3>, ...]"

DO NOT ADD ANY TEXT BEFORE OR AFTER THE BRACKETS. If no, answer ONLY in the following form:

"[]"

The contents of "tests.json" are:

{_insert_tests}

I am going to parse your input in my Python program, therefore, ONLY ANSWER IN THE FORM I GAVE YOU."""


def format_req_is_tested_prompt(
        tests: list[dict[str, str]],
        req: dict[str, str],
        prompt: str | None = None
    ) -> str:
    if prompt is None:
        prompt = _default_prompt

    return prompt \
        .replace(_insert_req, json.dumps(req)) \
        .replace(_insert_tests, json.dumps(tests, indent=2))
