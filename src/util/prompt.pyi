"""
Utility module for formatting prompts for REST-at.

Includes:
---------
`format_req_is_tested_prompt -> str` - A function that formats a prompt for checking whether a
requirement is tested or not.
"""


def format_req_is_tested_prompt(tests: list[dict[str, str]], req: dict[str, str]) -> str:
    """
    Formats a prompt for checking whether a requirement is tested or not.

    Parameters:
    -----------
    tests: list[dict[str, str]] - The list of tests to check.\n
    req: dict[str, str] - The requirements to check.

    Returns:
    --------
    `str` - The formatted prompt string.
    """
    ...
