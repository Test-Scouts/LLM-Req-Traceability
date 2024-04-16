"""
Utility module for abstracting REST.

Includes:
---------
`FieldMismatchError` - An error raised when trying to load malformed files.
`RESTSpecification` - A class for abstracting REST and filtering out malformed requirements and tests.
"""

from os import PathLike


class FieldMismatchError(Exception):
    """
    Error raised when trying to load REST specifications from malformed `.csv` files.
    """
    ...


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

    @staticmethod
    def load_specs(reqs_path: str | PathLike, tests_path: str | PathLike) -> RESTSpecification:
        """
        Load REST specifications from `.csv` files.
        The files must follow specific formats.

        Parameters:
        -----------
        reqs_path: str | PathLike - The path to the requiremnts file.\n
        tests_path: str | PathLike - The path to the tests file.

        Returns:
        --------
        `RESTSpecification` - A REST specification for the provided files.

        Raises:
        -------
        `FieldMismatchError` - If the required fields are missing in the `.csv` file.
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

    @property
    def n(self) -> int:
        """
        The number of requirement-test pairs in the specification.
        Equal to `len(reqs) * len(tests)`
        """
        ...
    
    @property
    def reqs(self) -> list[dict[str, str]]:
        """
        A copy of the requirements of the specification.
        """
        ...
    
    @property
    def tests(self) -> list[dict[str, str]]:
        """
        A copy the tests of the specification.
        """
        ...

    def to_gpt(self, model: str) -> tuple[dict[str, list[str]], tuple[int, int]]:
        """
        Sends REST data to a specified GPT model for REST alignment analysis.

        Parameters:
        -----------
        model: str - The GPT model to prompt.

        Returns:
        --------
        `tuple[dict[str, list[str]], tuple[int, int]]` - The REST alignment mapping from requirement to tests,
         and token usage as follows:\n
        `({<req ID>: [<test ID>...]}, (input tokens, output tokens))`\n
        """
        ...


    def to_local(self, model_name_or_path: str | PathLike) -> dict[str, list[str]]:
        """
        Sends REST data to a specified local model for REST alignment analysis.

        Parameters:
        -----------
        model_name_or_path: str | PathLike - The model to prompt.

        Returns:
        --------
        `dict[str, list[str]]` - The REST alignment mapping from requirement to tests as follows:\n
        `{<req ID>: [<test ID>...]}`
        """
        ...
