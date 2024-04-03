from __future__ import annotations
from os import PathLike
import copy
from transformers import AutoTokenizer, AutoModelForCausalLM, Conversation, PreTrainedTokenizer, PreTrainedTokenizerFast, PreTrainedModel
import torch
from typing import Final
from .model import *


class ModelLoadingException(Exception):
    def __init__(self, model_name_or_path: str | PathLike, *args):
        super().__init__(f"{model_name_or_path} is being loaded.", *args)


class Model:
    def __init__(
            self,
            tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast,
            model: PreTrainedModel,
            max_new_tokens: int
        ):
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
    def get(model_name_or_path: str | PathLike, max_new_tokens: int = None) -> Model | None:
        m: Model = Model._get(model_name_or_path)

        # Return None if the loading placeholder is present
        if m is Model._get_placeholder():
            return None

        # Return model if already loaded
        if m:
            return m
        
        if max_new_tokens is None:
            raise ValueError("Cannot load model without max_new_tokens.")
        
        # Add a placeholder in the dict to prevent additional loads
        Model._MODELS[model_name_or_path] = Model._get_placeholder()

        # Load the model and its tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        tokenizer.chat_template

        model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(model_name_or_path, torch_dtype=torch.float16, device_map="auto")
        model.eval()

        Model._MODELS[model_name_or_path] = m = Model(tokenizer, model, max_new_tokens)

        return m
    
    def _gen_prompt(self, user_prompt: str, system_prompt: str) -> str:
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

        return f"\nSystem definition:\n{system_prompt} \nEnd system definition.\n\n{user_prompt}"
    
    def prompt(
            self,
            history: list[dict[str, str]] | Conversation,
            prompt: str,
            system_prompt: str = _SYSTEM_PROMPT
        ) -> str:
        history.append({"role": "user", "content": self._gen_prompt(prompt, system_prompt)})
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



class Session:
    def __init__(
            self,
            name: str,
            model_name_or_path: str | PathLike,
            max_new_tokens: int,
            system_prompt: str
        ):
        self.name: str = name
        self.model: Model = Model.get(model_name_or_path, max_new_tokens)

        # Don't instantiate if model is loading
        if not self.model:
            raise ModelLoadingException(model_name_or_path)

        self._system_prompt: str = system_prompt
        self._history: list[dict[str, str]] = []

    _SESSIONS: dict[str, Session] = {}

    @staticmethod
    def create(
        name: str,
        model_name_or_path: str | PathLike,
        max_new_tokens: int,
        system_prompt: str=Model._SYSTEM_PROMPT
    ) -> Session:
        session: Session = Session.get(name)

        if session:
            return session

        session = Session(name, model_name_or_path, max_new_tokens, system_prompt)

        Session._SESSIONS[name] = session
        return session

    @staticmethod
    def get(name: str) -> Session | None:
        return Session._SESSIONS.get(name, None)
    
    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, system_prompt: str) -> None:
        if not system_prompt:
            system_prompt = Model._SYSTEM_PROMPT
        self._system_prompt = system_prompt
    
    def prompt(self, prompt: str, ephemeral: bool = False) -> str:
        res: str = self.model.prompt(self._history, prompt, self._system_prompt)

        # Pop twice to remove the newly added user and assistant messages if ephemeral
        if ephemeral:
            self._history.pop()
            self._history.pop()
        
        return res

    def clear(self) -> None:
        self._history = []

    @property
    def history(self) -> list[dict[str, str]]:
        return copy.deepcopy(self._history)

    def delete(self) -> None:
        del Session._SESSIONS[self.name]
