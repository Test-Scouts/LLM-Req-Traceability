from model import Session


class RESTSpecification:
    def __init__(self, reqs: set[str], tests: set[str]) -> None:
        self._reqs: set[str] = set(reqs)
        self._tests: set[str] = set(tests)

    def check_req(self, req: str) -> bool:
        return req in self._reqs
    
    def check_test(self, test: str) -> bool:
        return test in self._tests

    def filter_reqs(self, reqs: set[str]) -> None:
        reqs.intersection_update(self._reqs)
    
    def filter_tests(self, tests: set[str]) -> None:
        tests.intersection_update(self._tests)

    @property
    def n(self) -> int:
        return len(self._reqs) * len(self._tests)
    
    @property
    def reqs(self) -> frozenset[str]:
        return frozenset(self._reqs)
    
    @property
    def tests(self) -> frozenset[str]:
        return frozenset(self._tests)
    
    def to_gpt(self, model: str, reqs: list[dict[str, str]], tests: list[dict[str, str]]) -> dict[str, list[str]]:
        # TODO: Implement based on send_data_gpt
        pass

    def to_local(self, session: Session, reqs: list[dict[str, str]], tests: list[dict[str, str]]) -> dict[str, list[str]]:
        # TODO: Implement based on send_data
        pass
