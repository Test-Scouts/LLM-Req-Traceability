from unittest import TestCase

from .rest import *


class TestIntermediateOutputParser(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        reqs: str = "ID,Feature,\"Description\"\n" \
                  + "1,test,test"
        tests: str = "ID,Purpose,\"Test steps\"\n" \
                   + "1,test,test"
        self.specs: RESTSpecification = RESTSpecification.load_specs_from_str(reqs, tests)
    
    def test_parse_json(self):
        raw_res: str = "{\n" \
                 + "  \"requirementID\": \"R-0\",\n" \
                 + "  \"tests\": \"T-0\"\n" \
                 + "}"
        res: list[str] = self.specs._parse_intermediary_output(raw_res)
        
        self.assertListEqual(
            res,
            ["1"]
        )

    def test_parse_list(self):
        raw_res: str = "[\"T-0\"]"
        res: list[str] = self.specs._parse_intermediary_output(raw_res)

        self.assertListEqual(
            res,
            ["1"]
        )
