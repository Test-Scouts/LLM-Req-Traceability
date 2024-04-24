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

    Properties:
    -----------
    `readonly n: int` - The number of requirement-test pairs in the specification.
    `readonly reqs: list[dict[str, str]]` - A copy of the requirements of the specification.
    `readonly tests: list[dict[str, str]]` - A copy of the tests of the specification.

    Methods:
    --------
    `static load_specs -> RESTSpecification` - Loads specifications from REST files.
    `check_req -> bool` - Check if a requirement ID exists within a specification.
    `check_test -> bool` - Check if a test ID exists within a specification.
    `to_gpt -> dict[str, list[str]]` - Sends REST data to an OpenAI model and returns the detected links in the following format:
    ```json
    {
      "<requirement ID>": ["<test ID>"...]
      ...
    }
    ```
    `to_local -> tuple[dict[str, list[str]], tuple[int, int]]` - Sends REST data to a local model and returns the detected links and token usage in the following format:
    ```json
    (
      {
        "<requirement ID>": ["<test ID>"...]
        ...
      },
      (
        <input tokens>,
        <output tokens>
      )
    )
    ```
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
        ```json
        (
          {
            "<requirement ID>": ["<test ID>"...]
            ...
          },
          (
            <input tokens>,
            <output tokens>
          )
        )
        ```
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
        `dict[str, list[str]]` - The REST alignment mapping from requirement to tests as follows:\n
        ```json
        {
          "<requirement ID>": ["<test ID>"...]
          ...
        }
        ```
        """
        ...
