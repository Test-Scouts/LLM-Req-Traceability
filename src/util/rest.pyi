"""
Utility module for abstracting REST.

Includes:
---------
`RESTSpecification` - A class for abstracting REST and filtering out malformed requirements and tests.
"""

from .model import Session


class RESTSpecification:
    """
    A class for abstracting REST and filtering out malformed requirements and tests.

    Methods:
    --------
    `check_req -> bool` - Check if a requirement ID exists within a specification.\n
    `check_test -> bool` - Check if a test ID exists within a specification.\n
    `filter_reqs -> None` - Filters out all requirement IDs which do not exist within a specification.\n
    `filter_tests -> None` - Filters out all test IDs which do not exist within a specification.
    """

    def __init__(self, reqs: set[str], tests: set[str]) -> None:
        """
        A class for abstracting REST and filtering out malformed requirements and tests.
        """
        ...

    def check_req(self, req: str) -> bool:
        """
        Check if a requirement ID exists within the specification.
        
        Parameters:
        -----------
        req: str - The requirement ID to check.

        Returns:
        --------
        `bool` - Whether the REST specification contains `req` or not.
        """
        ...
    
    def check_test(self, test: str) -> bool:
        """
        Check if a test ID exists within the specification.
        
        Parameters:
        -----------
        req: str - The requirement ID to check.

        Returns:
        --------
        `bool` - Whether the REST specification contains `req` or not.
        """
        ...

    def filter_reqs(self, reqs: set[str]) -> None:
        """
        Filters out requirement IDs that do not exist in the specification.
        
        Parameters:
        -----------
        reqs: str - The requirement IDs to filter.
        """
        ...
    
    def filter_tests(self, tests: set[str]) -> None:
        """
        Filters out test IDs that do not exist in the specification.
        
        Parameters:
        -----------
        tests: str - The test IDs to filter.
        """
        ...

    @property
    def n(self) -> int:
        """
        The number of requirement-test pairs in the specification.
        Equal to `len(reqs) * len(tests)`
        """
        ...
    
    @property
    def reqs(self) -> frozenset[str]:
        """
        A frozen set of the requirement IDs of the specification.
        """
        ...
    
    @property
    def tests(self) -> frozenset[str]:
        """
        A frozen set of the test IDs of the specification.
        """
        ...

    def to_gpt(self, model: str, reqs: list[dict[str, str]], tests: list[dict[str, str]]) -> dict[str, list[str]]:
        """
        Sends REST data to a specified GPT model for REST alignment analysis.

        Parameters:
        -----------
        model: str - The GPT model to prompt.\n
        reqs: list[dict[str, str]] - The list of requirements in the REST alignment analysis.
        Each entry must conform to the following shape:\n
        `{"ID": <req ID: str>, "Feature": <feature: str>, "Description": <req description: str>}`\n
        tests: list[dict[str, str]] - The list of tests in the REST alignment analysis.
        Each entry must conform to the following shape:\n
        `{"ID": <test ID: str>, "Purpose": <purpose: str>, "Test steps": <test steps: str>}`

        Returns:
        --------
        `dict[str, list[str]]` - The REST alignment mapping from requirement to tests as follows:\n
        `{<req ID>: [<test ID>...]}`
        """
        ...


    def to_local(self, session: Session, reqs: list[dict[str, str]], tests: list[dict[str, str]]) -> dict[str, list[str]]:
        """
        Sends REST data to a specified local model for REST alignment analysis.

        Parameters:
        -----------
        session: Session - The session to prompt.\n
        reqs: list[dict[str, str]] - The list of requirements in the REST alignment analysis.
        Each entry must conform to the following shape:\n
        `{"ID": <req ID: str>, "Feature": <feature: str>, "Description": <req description: str>}`\n
        tests: list[dict[str, str]] - The list of tests in the REST alignment analysis.
        Each entry must conform to the following shape:\n
        `{"ID": <test ID: str>, "Purpose": <purpose: str>, "Test steps": <test steps: str>}`

        Returns:
        --------
        `dict[str, list[str]]` - The REST alignment mapping from requirement to tests as follows:\n
        `{<req ID>: [<test ID>...]}`
        """
        ...
