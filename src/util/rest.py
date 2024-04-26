from __future__ import annotations
from copy import deepcopy
import datetime
from os import PathLike
import csv
import json
from io import StringIO

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

    def to_gpt(self, model: str) -> tuple[dict[str, list[str]], tuple[int, int]]:
        client: OpenAI = OpenAI()

        input_tokens: int = 0
        output_tokens: int = 0

        res: dict[str, list[str]] = {}

        for req in self._reqs:
            history = [{"role": "user", "content": format_req_is_tested_prompt(self._tests, req)}]
            completion: ChatCompletion = client.chat.completions.create(
                model=model,
                messages=history,
                temperature=0.1
            )
            r: str = completion.choices[0].message.content

            # Simple JSON finder
            # Slice from the first "{" to the last "}"
            r = r[r.find("{"):r.rfind("}") + 1]
            curr_res: dict[str, str] = json.loads(r)
            links: list[str]

            try:
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

            # Use the requirement ID instead of its internal index
            req_id: str = self \
                ._reqs_index[int(req["ID"].replace(RESTSpecification._REQ_INDEX_PREFIX, ""))]
            res[req_id] = links

            input_tokens += completion.usage.prompt_tokens
            output_tokens += completion.usage.completion_tokens

        return (res, (input_tokens, output_tokens))

    def to_local(self, model_name_or_path: str | PathLike, max_new_tokens: int) -> dict[str, list[str]]:
        id_: str = f"{id(self)}-{datetime.datetime.now().timestamp()}"
        session: Session = Session.create(
            id_,
            model_name_or_path,
            max_new_tokens,
            self._system_prompt
        )

        res: dict[str, list[str]] = {}

        for req in self._reqs:
            r: str = session.prompt(format_req_is_tested_prompt(self._tests, req), True)

            # Simple JSON finder
            # Slice from the first "{" to the last "}"
            r = r[r.find("{"):r.rfind("}") + 1]
            curr_res = json.loads(r)
            links: list[str]

            try:
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

            # Use the requirement ID instead of its internal index
            req_id: str = self \
                ._reqs_index[int(req["ID"].replace(RESTSpecification._REQ_INDEX_PREFIX, ""))]
            res[req_id] = links

        session.delete()
        return res

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {{\n" \
             + f"reqs: {json.dumps(self._reqs, indent=2)}\n" \
             + f"reqs_index: {self._reqs_index}\n" \
             + f"tests: {json.dumps(self._tests, indent=2)}\n" \
             + f"tests_index: {self._tests_index}\n" \
             + "}"
