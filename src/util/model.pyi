"""
Utility module for handling models.

Includes:
---------
`Model` - A class abstracting pretrained models, providing methods to load, retrieve, and prompt a model.
"""
from os import PathLike
from transformers import Conversation


class Model:
    """
    A class abstracting pretrained models, providing functions to load, retrieve, and prompt a model.

    Methods:
    --------
    `static load -> Model` - Loads a given model if not already loaded and returns the model.\n
    `static get -> Model` - Gets a loaded model or `None` if not loaded.\n
    `prompt -> str` - Prompts the model and returns the response.
    """

    @staticmethod
    def get(model_name_or_path: str | PathLike, max_new_tokens: int) -> Model | None:
        """
        Loads a specified model if not already loaded.

        Parameters:
        -----------
        model_name_or_path: str | PathLike - The model to load. Can be either a model name from Hugging Face Hub or a path to a local model.
        max_new_tokens: int - The `max_new_tokens` parameter used when generating.
        Returns:
        --------
        `Model | None` The model that was loaded. None if the specified model is being loaded.
        """
        ...

    def prompt(self, history: list[dict[str, str]] | Conversation, prompt: str) -> str:
        """
        Prompts a the model and gets the response.

        Parameters:
        -----------
        history: list[dict[str, str]] | Conversation - The conversation history. Must adhere to model constraints.
        prompt: str - The user prompt to send to the model. Must

        Returns:
        --------
        `str` - The response from the model if the model is loaded, else `None`.

        Raises:
        -------
        `ValueError` if `user_prompt` is empty, `None`, or consists of only whitespace characters.
        """
        ...
