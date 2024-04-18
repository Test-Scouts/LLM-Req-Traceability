from __future__ import annotations
from copy import deepcopy
import datetime
from os import PathLike
import csv
import json

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

        self._system_prompt: str = "You are a helpful AI assistant"

    @staticmethod
    def load_specs(reqs_path: str | PathLike, tests_path: str | PathLike) -> RESTSpecification:
        # Load requirements file and filter the desired fields
        req_list: list[dict[str, str]] = []
        req_index: list[str] = []
        with open(reqs_path) as reqs:
            fields: set[str] = {
                "ID",
                "Feature",
                "Description"
            }
            reader: csv.DictReader = csv.DictReader(reqs)

            csv_fields: set[str] = set(reader.fieldnames)
            # Validate fields
            if fields - csv_fields != set():
                raise FieldMismatchError(fields, fields & csv_fields)

            for i, row in enumerate(reader):
                r: dict[str, str] = {k: row[k] for k in row.keys() if k in fields}

                # Substitute the requirement ID with an index
                id_: str = r["ID"]
                r["ID"] = str(i)

                req_list.append(r)
                req_index.append(id_)

        # Load tests file and filter the desired fields
        test_list: list[dict[str, str]] = []
        test_index: list[str] = []
        with open(tests_path) as tests:
            fields: set[str] = {
                "ID",
                "Purpose",
                "Test steps"
            }
            reader: csv.DictReader = csv.DictReader(tests)

            csv_fields: set[str] = set(reader.fieldnames)
            # Validate fields
            if fields - csv_fields != set():
                raise FieldMismatchError(fields, fields & csv_fields)

            for i, row in enumerate(reader):
                t: dict[str, str] = {k: row[k] for k in row.keys() if k in fields}

                # Substitute the requirement ID with an index
                id_: str = t["ID"]
                t["ID"] = str(i)

                test_list.append(t)
                test_index.append(id_)

        return RESTSpecification((req_list, req_index), (test_list, test_index))

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
                links = curr_res["tests"].replace(" ", "").split(",") if curr_res["tests"] else []
                links = [self._tests_index[int(test)] for test in links]
            except:
                links = []
            
            # Use the requirement ID instead of its internal index
            res[self._reqs_index[int(req["ID"])]] = links

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
                links = curr_res["tests"].replace(" ", "").split(",") if curr_res["tests"] else []
                links = [self._tests_index[int(test)] for test in links]
            except:
                links = []
            
            # Use the requirement ID instead of its internal index
            res[self._reqs_index[int(req["ID"])]] = links

        session.delete()
        return res

    def __str__(self) -> str:
        return f"{self.__class__.__name__} {{\n" \
             + f"reqs: {json.dumps(self._reqs, indent=2)}\n" \
             + f"reqs_index: {self._reqs_index}\n" \
             + f"tests: {json.dumps(self._tests, indent=2)}\n" \
             + f"tests_index: {self._tests_index}\n" \
             + "}"
