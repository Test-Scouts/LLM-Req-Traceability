from __future__ import annotations
from copy import deepcopy
import datetime
from os import PathLike
import csv
import json
from io import StringIO
import traceback
from typing_extensions import override

from openai import OpenAI
from openai.types.chat import ChatCompletion

from .prompt import format_req_is_tested_prompt
from .model import Session
from .rest import *


class FieldMismatchError(Exception):
    def __init__(self, expected: set[str], got: set[str], *args: object) -> None:
        super().__init__(f"Mismatched field names.\n\tExpected: {expected}\n\tGot: {got}", *args)
        self.expected: set[str] = expected
        self.got: set[str] = got


class Response:
    def __init__(self, links: dict[str, list[str]], err: dict[str, list[str]]) -> None:
        self.links: dict[str, list[str]] = links
        self.err: dict[str, list[str]] = err

    @property
    def as_dict(self) -> dict:
        return {
            "links": deepcopy(self.links),
            "err": deepcopy(self.err)
        }


class GPTResponse(Response):
    def __init__(self, links: dict[str, list[str]], err: dict[str, list[str]], tokens: tuple[int, int]) -> None:
        super().__init__(links, err)
        self.input_tokens: int = tokens[0]
        self.output_tokens: int = tokens[1]

    @override
    @property
    def as_dict(self) -> dict:
        return super() \
            .as_dict \
            .update({
                "input_tokens": self.input_tokens,
                "output_tokens": self.output_tokens
            })


class RESTSpecification:
    _REQ_INDEX_PREFIX: str = "R-"
    _TEST_INDEX_PREFIX: str = "T-"

    _REQ_FIELDS: set[str] = {
        "ID",
        "Feature",
        "Description"
    }

    _TEST_FIELDS: set[str] = {
        "ID",
        "Purpose",
        "Test steps"
    }

    def __init__(
            self,
            reqs: tuple[list[dict[str, str]], list[str]],
            tests: tuple[list[dict[str, str]], list[str]]
        ) -> None:
        self._reqs: list[dict[str, str]]
        self._tests: list[dict[str, str]]
        self._reqs_index: list[str]
        self._tests_index: list[str]

        self._reqs, self._reqs_index = reqs
        self._tests, self._tests_index = tests

        self._system_prompt: str = "You are a helpful assistant."

    @staticmethod
    def load_specs_from_str(reqs: str, tests: str) -> RESTSpecification:
        # Load requirements and filter the desired fields

        # Wrap req data with StringIO to make it act like a file
        req_data: StringIO = StringIO(reqs)

        req_list: list[dict[str, str]] = []
        req_index: list[str] = []
        req_fields: set[str] = RESTSpecification._REQ_FIELDS
        req_reader: csv.DictReader = csv.DictReader(req_data)

        csv_req_fields: set[str] = set(req_reader.fieldnames)
        # Validate fields
        if req_fields - csv_req_fields != set():
            raise FieldMismatchError(req_fields, req_fields & csv_req_fields)

        for i, row in enumerate(req_reader):
            r: dict[str, str] = {k: row[k] for k in row.keys() if k in req_fields}

            # Substitute the requirement ID with an index
            id_: str = r["ID"]
            r["ID"] = f"{RESTSpecification._REQ_INDEX_PREFIX}{i}"

            req_list.append(r)
            req_index.append(id_)

        # Load tests and filter the desired fields

        # Wrap test data with StringIO to make it act like a file
        test_data: StringIO = StringIO(tests)

        test_list: list[dict[str, str]] = []
        test_index: list[str] = []
        test_fields: set[str] = RESTSpecification._TEST_FIELDS
        test_reader: csv.DictReader = csv.DictReader(test_data)

        csv_test_fields: set[str] = set(test_reader.fieldnames)
        # Validate fields
        if test_fields - csv_test_fields != set():
            raise FieldMismatchError(test_fields, test_fields & csv_test_fields)

        for i, row in enumerate(test_reader):
            t: dict[str, str] = {k: row[k] for k in row.keys() if k in test_fields}

            # Substitute the requirement ID with an index
            id_: str = t["ID"]
            t["ID"] = f"{RESTSpecification._TEST_INDEX_PREFIX}{i}"

            test_list.append(t)
            test_index.append(id_)

        return RESTSpecification((req_list, req_index), (test_list, test_index))

    @staticmethod
    def load_specs(reqs_path: str | PathLike, tests_path: str | PathLike) -> RESTSpecification:
        reqs: str
        with open(reqs_path) as f:
            reqs = f.read()

        tests: str
        with open(tests_path) as f:
            tests = f.read()

        return RESTSpecification.load_specs_from_str(reqs, tests)

    def check_req(self, req: str) -> bool:
        return req in self._reqs_index

    def check_test(self, test: str) -> bool:
        return test in self._tests_index

    @property
    def n(self) -> int:
        return len(self._reqs) * len(self._tests)

    @property
    def reqs(self) -> list[dict[str, str]]:
        return deepcopy(self._reqs)

    @property
    def tests(self) -> list[dict[str, str]]:
        return deepcopy(self._tests)

    def to_gpt(self, model: str) -> GPTResponse:
        client: OpenAI = OpenAI()

        input_tokens: int = 0
        output_tokens: int = 0

        res: dict[str, list[str]] = {}
        err: dict[str, list[str]] = {}

        SEED = 0
        if model == "gpt-3.5-turbo-0125":
            system_fingerprint = "fp_3b956da36b"
        elif model == "gpt-3.5-turbo-0126":
            system_fingerprint = "fp_ea6eb70039"

        for req in self._reqs:
            history = [{"role": "user", "content": format_req_is_tested_prompt(self._tests, req)}]
            completion: ChatCompletion = client.chat.completions.create(
                model=model,
                messages=history,
                temperature=0.1,
                seed = SEED,
                system_fingerprint = system_fingerprint,

            )

            raw_res: str = completion.choices[0].message.content


            #######################################################
            # Uncomment to print system fingerprint and seed used
            #######################################################
            #system_fingerprint = completion.system_fingerprint 
            #if not_printed:
            #    print(f'system fingerprint = {system_fingerprint} and seed = {SEED}')
            #    not_printed = False

            curr_res: str
            links: list[str]

            # Use the requirement ID instead of its internal index
            req_id: str = self \
                ._reqs_index[int(req["ID"].replace(RESTSpecification._REQ_INDEX_PREFIX, ""))]

            try:
                # Simple JSON finder
                # Slice from the first "{" to the last "}"
                curr_res = raw_res[raw_res.find("{"):raw_res.rfind("}") + 1]
                curr_res: dict[str, str] = json.loads(curr_res)

                # Substitute the test indices back to the test IDs
                links = curr_res["tests"] \
                    .replace(" ", "") \
                    .split(",") \
                    if curr_res["tests"] else []
                links = [
                    self._tests_index[int(test.replace(RESTSpecification._TEST_INDEX_PREFIX, ""))]
                    for test in links
                ]
            except:
                links = []
                # Log error in response
                err[req_id] = [traceback.format_exc(), raw_res]

            res[req_id] = links

            input_tokens += completion.usage.prompt_tokens
            output_tokens += completion.usage.completion_tokens

        return GPTResponse(res, err, (input_tokens, output_tokens))

    def to_local(self, model_name_or_path: str | PathLike, max_new_tokens: int) -> Response:
        id_: str = f"{id(self)}-{datetime.datetime.now().timestamp()}"
        session: Session = Session.create(
            id_,
            model_name_or_path,
            max_new_tokens,
            self._system_prompt
        )

        res: dict[str, list[str]] = {}
        err: dict[str, list[str]] = {}

        for req in self._reqs:
            raw_res: str = session.prompt(format_req_is_tested_prompt(self._tests, req), True)

            curr_res: str
            links: list[str]

            # Use the requirement ID instead of its internal index
            req_id: str = self \
                ._reqs_index[int(req["ID"].replace(RESTSpecification._REQ_INDEX_PREFIX, ""))]

            try:
                # Simple JSON finder
                # Slice from the first "{" to the last "}"
                curr_res = raw_res[raw_res.find("{"):raw_res.rfind("}") + 1]
                curr_res = json.loads(curr_res)

                # Substitute the test indices back to the test IDs
                links = curr_res["tests"] \
                    .replace(" ", "") \
                    .split(",") \
                    if curr_res["tests"] else []
                links = [
                    self._tests_index[int(test.replace(RESTSpecification._TEST_INDEX_PREFIX, ""))]
                    for test in links
                ]
            except:
                links = []
                # Log error in response
                err[req_id] = [traceback.format_exc(), raw_res]

            res[req_id] = links

        session.delete()
        return Response(res, err)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {{\n" \
             + f"reqs: {json.dumps(self._reqs, indent=2)}\n" \
             + f"reqs_index: {self._reqs_index}\n" \
             + f"tests: {json.dumps(self._tests, indent=2)}\n" \
             + f"tests_index: {self._tests_index}\n" \
             + "}"
