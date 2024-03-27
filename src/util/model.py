from __future__ import annotations
from os import PathLike
from transformers import AutoTokenizer, AutoModelForCausalLM, Conversation, PreTrainedTokenizer, PreTrainedTokenizerFast, PreTrainedModel
import torch
from typing import Final
from .model import *


class Model:
    def __init__(self, tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast, model: PreTrainedModel, max_new_tokens: int):
        self.tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast = tokenizer
        self.model: PreTrainedModel = model
        self.max_new_tokens: int = max_new_tokens

    _MODELS: Final[dict[str | PathLike, Model]] = {}

    _PLACEHOLDER: Model = None

    # Instruction suffix
    _INST_SUFFIX: Final[str] = "[/INST]"
    _INST_SUFFIX_LEN : Final[int] = len(_INST_SUFFIX)

    # System prompt used for REST-at
    _SYSTEM_PROMPT: Final[str] = "You are a helpful AI called Kalle."

    @staticmethod
    def _get_placeholder() -> Model:
        """
        Retrieves the placeholder for loading models.

        Returns:
        --------
        `Model` - An empty placeholder model.
        """
        if not Model._PLACEHOLDER:
            Model._PLACEHOLDER = Model(None, None, None)
        return Model._PLACEHOLDER

    @staticmethod
    def _get(model_name_or_path: str | PathLike):
        """
        Gets a model if loaded, else `None`

        Parameters:
        -----------
        model_name_or_path: str | PathLike - The model to get. Can be either a model name from Hugging Face Hub or a path to a local model.

        Returns:
        --------
        `Model | None` The tokenizer and the model itself if loaded, else None.
        """
        return Model._MODELS.get(model_name_or_path, None)

    @staticmethod
    def get(model_name_or_path: str | PathLike, max_new_tokens: int) -> Model | None:
        m: Model = Model._get(model_name_or_path)

        # Return None if the loading placeholder is present
        if m is Model._get_placeholder():
            return None

        # Return model if already loaded
        if m:
            return m
        
        # Add a placeholder in the dict to prevent additional loads
        Model._MODELS[model_name_or_path] = Model._get_placeholder()

        # Load the model and its tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(model_name_or_path, torch_dtype=torch.float16, device_map="auto")
        model.eval()

        Model._MODELS[model_name_or_path] = m = Model(tokenizer, model, max_new_tokens)

        return m
    
    @staticmethod
    def _gen_prompt(user_prompt: str, system_prompt: str=_SYSTEM_PROMPT) -> str:
        """
        Generate a prompt using a predefined system prompt.

        Parameters:
        -----------
        `user_prompt: str` - The user prompt. Must consist of at least 1 non-whitespace character.

        Returns:
        --------
        `str` - A formatted prompt.

        Raises:
        -------
        `ValueError` if `user_prompt` is empty, `None`, or consists of only whitespace characters.
        """
        prompt: str = user_prompt.strip()

        if not prompt:
            raise ValueError("User prompt must consist of at least 1 non-whitespace character.")

        return f"[SYS] {system_prompt} [/SYS]\n\n{user_prompt}"

    def prompt(self, history: list[dict[str, str]] | Conversation, prompt: str) -> str:
        history.append({"role": "user", "content": Model._gen_prompt(prompt)})
        input_ids: str | list[int] = self.tokenizer.apply_chat_template(history, return_tensors="pt").to("cuda")

        # Reset prompt to the raw input
        history[-1]["content"] = prompt

        outputs = self.model.generate(
            input_ids,
            max_new_tokens=self.max_new_tokens,
            do_sample=True,
            temperature=0.1
        )

        raw_res: str = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Cut out the instruction section of the output
        res: str = raw_res[(raw_res.rfind(Model._INST_SUFFIX) + Model._INST_SUFFIX_LEN)::].strip()

        # Append response to history
        history.append({"role": "assistant", "content": res})
        return res
