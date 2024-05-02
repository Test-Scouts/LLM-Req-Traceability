"""
Core module for formatting prompts for REST-at.

Includes:
---------
`format_req_is_tested_prompt -> str` - A function that formats a prompt for checking whether a
requirement is tested or not.
"""


def format_req_is_tested_prompt(
        tests: list[dict[str, str]],
        req: dict[str, str],
        prompt: str | None = None
    ) -> str:
    """
    Formats a prompt for checking whether a requirement is tested or not.

    Parameters:
    -----------
    tests: list[dict[str, str]] - The list of tests to check.\n
    req: dict[str, str] - The requirements to check.\n
    prompt: str | None - The prompt to be used.
    Include `{req}` in place of the requirement and `{tests}` in place of the tests.

    Returns:
    --------
    `str` - The formatted prompt string.
    """
    ...
