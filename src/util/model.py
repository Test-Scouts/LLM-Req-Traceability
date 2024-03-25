import os
from transformers import AutoTokenizer, AutoModelForCausalLM, PreTrainedTokenizer, PreTrainedTokenizerFast, PreTrainedModel
import torch
from typing import Final
from model import *


# ModelData: TypeAlias = tuple[PreTrainedTokenizer | PreTrainedTokenizerFast, PreTrainedModel]
_MODELS: Final[dict[str | os.PathLike, ModelData]] = {}


def load_model(model_name_or_path: str | os.PathLike) -> ModelData:
    model_data: ModelData = _MODELS.get(model_name_or_path, None)

    # Return if the specified model has already been loaded
    if model_data:
        return model_data

    # Load the model and its tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(model_name_or_path, torch_dtype=torch.float16, device_map="auto")

    _MODELS[model_name_or_path] = (tokenizer, model)

    return tokenizer, model

def get_model(model_name_or_path: str | os.PathLike) -> ModelData | None:
    return _MODELS.get(model_name_or_path)
