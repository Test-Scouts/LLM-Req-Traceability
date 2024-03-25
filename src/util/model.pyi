import os
from transformers import PreTrainedTokenizer, PreTrainedTokenizerFast, PreTrainedModel
from typing import TypeAlias


ModelData: TypeAlias = tuple[PreTrainedTokenizer | PreTrainedTokenizerFast, PreTrainedModel]


def load_model(model_name_or_path: str | os.PathLike) -> ModelData:
    """
    Loads a specified model if not already loaded.

    Parameters:
    -----------
    `model_name_or_path: str | PathLike` - The model to load. Can be either a model name from Hugging Face Hub or a path to a local model.

    Returns:
    --------
    `tuple[PreTrainedTokenizer | PreTrainedTokenizerFast, PreTrainedModel]` The tokenizer and the model itself.
    """
    pass

def get_model(model_name_or_path: str | os.PathLike) -> ModelData | None:
    """
    Gets a model if loaded, else `None`

    Parameters:
    -----------
    `model_name_or_path: str | PathLike` - The model to get. Can be either a model name from Hugging Face Hub or a path to a local model.

    Returns:
    --------
    `tuple[PreTrainedTokenizer | PreTrainedTokenizerFast, PreTrainedModel] | None` The tokenizer and the model itself if loaded, else None.
    """
    pass
