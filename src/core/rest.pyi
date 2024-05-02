"""
Core module for abstracting REST.

Includes:
---------
`FieldMismatchError` - An error raised when trying to load malformed files.\n
`RESTSpecification` - A class for abstracting REST and filtering out malformed requirements and tests.
"""

from os import PathLike
from typing_extensions import Never, override


class FieldMismatchError(Exception):
    """
    Error raised when trying to load REST specifications from malformed `.csv` files.
    """
    ...


class Response:
    """
    Responses for calls to local models.

    Attributes:
    -----------
    `links: dict[str, list[str]]` - The detected REST trace links mapped from requirements to lists of tests.\n
    `err: dict[str, str]` - Errors encountered during the run mapped from requirement to the traceback.

    Properties:
    -----------
    `as_dict: dict` - A dict representation of the response object.
    """
    def __init__(self, *args) -> Never:
        self.links: dict[str, list[str]]
        """The detected REST trace links mapped from requirements to lists of tests."""
        self.err: dict[str, list[str]]
        """
        Errors encountered during the run mapped from requirement to the traceback.
        Includes the error and the response. (`[err, res]`)
        """
        ...

    @property
    def as_dict(self) -> dict:
        """
        A dict representation of the response object.
        """
        ...


class GPTResponse(Response):
    """
    Responses for calls to OpenAI's API.

    Attributes:
    -----------
    `links: dict[str, list[str]]` - The detected REST trace links mapped from requirements to lists of tests.\n
    `err: dict[str, str]` - Errors encountered during the run mapped from requirement to the traceback.\n
    `input_tokens: int` - The amount of tokens sent to the API.\n
    `output_tokens: int` - The amount of tokens generated through the API.

    Properties:
    -----------
    `as_dict: dict` - A dict representation of the response object.
    """
    def __init__(self, *args) -> Never:
        self.input_tokens: int
        """The amount of tokens sent to the API."""
        self.output_tokens: int
        """The amount of tokens generated through the API."""
        ...

    @override
    @property
    def to_dict(self) -> dict:
        """
        A dict representation of the response object.
        """
        ...


class RESTSpecification:
    """
    A class for abstracting REST and filtering out malformed requirements and tests.

    Properties:
    -----------
    `readonly n: int` - The number of requirement-test pairs in the specification.\n
    `readonly reqs: list[dict[str, str]]` - A copy of the requirements of the specification.\n
    `readonly tests: list[dict[str, str]]` - A copy of the tests of the specification.\n
    `system_prompt: str` - The system prompt to use when prompting a model.\n
    `prompt: str | None` - The prompt to use when prompting a model. Defaults to a predefined prompt.

    Methods:
    --------
    `static load_specs_from_str -> RESTSpecification - Loads specifications from REST strings. MUST USE CSV FORMAT!\n
    `static load_specs -> RESTSpecification` - Loads specifications from REST files. MUST USE CSV FORMAT!\n
    `check_req -> bool` - Check if a requirement ID exists within a specification.\n
    `check_test -> bool` - Check if a test ID exists within a specification.\n
    `to_gpt -> GPTResponse` - Sends REST data to an OpenAI model and returns a response object containing REST mapping, error data, and token usage.\n
    `to_local -> Response` - Sends REST data to a local model and returns A response object containing REST mapping and error data.
    """

    @staticmethod
    def load_specs_from_str(reqs: str, tests: str) -> RESTSpecification:
        """
        Load REST specifications from csv strings.
        The strings must follow specific formats.

        Parameters:
        -----------
        reqs: str - The requiremnts string.\n
        tests: str - The tests string.

        Returns:
        --------
        `RESTSpecification` - A REST specification for the provided files.

        Raises:
        -------
        `FieldMismatchError` - If the required fields are missing in the `.csv` file.
        """
        ...

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
        Always equal to `len(reqs) * len(tests)`
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

    @property
    def system_prompt(self) -> str:
        """
        The system prompt to use when prompting a model.
        """
        ...

    @system_prompt.setter
    def system_prompt(self, new) -> None:
        ...

    @property
    def prompt(self) -> str:
        """
        The prompt to use when prompting a model. Defaults to a predefined prompt.
        """
        ...

    @prompt.setter
    def prompt(self, new) -> None:
        ...

    def to_gpt(self, model: str) -> tuple[dict[str, list[str]], tuple[int, int]]:
        """
        Sends REST data to a specified GPT model for REST alignment analysis.

        Parameters:
        -----------
        model: str - The GPT model to prompt.

        Returns:
        --------
        `GPTResponse` - A response object containing REST mapping, error data, and token usage.
        """
        ...


    def to_local(self, model_name_or_path: str | PathLike, max_new_tokens: int) -> dict[str, list[str]]:
        """
        Sends REST data to a specified local model for REST alignment analysis.

        Parameters:
        -----------
        model_name_or_path: str | PathLike - The model to prompt.\n
        max_new_tokens: int - The `max_new_tokens` parameter used when generating.

        Returns:
        --------
        `Response` - A response object containing REST mapping and error data.
        """
        ...
