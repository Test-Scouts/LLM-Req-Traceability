from __future__ import annotations
from os import PathLike
import copy
from typing_extensions import deprecated

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BatchEncoding,
    Conversation,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
    PreTrainedModel
)
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
    def _get(model_name_or_path: str | PathLike) -> Model | None:
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

        model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        model.eval()

        Model._MODELS[model_name_or_path] = m = Model(tokenizer, model, max_new_tokens)

        return m
    
    def _apply_chat_template(self, messages: list[dict[str, str]]) -> BatchEncoding:
        """
        Applies a pre-defined chat template to a message history and tokenizes it.

        Parameters:
        -----------
        messages: list[dict[str, str]] - The message history.

        Returns:
        --------
        `BatchEncoding` - The encoded input.

        Raises:
        -------
        `ValueError` if `message["content"]` is empty or consists of only whitespace characters for any message.
        """
        chat: str = self.tokenizer.bos_token

        # Apply template

        # Check for system message in the message history
        # Use the default one in there is no system message
        sys_message: str = Model._SYSTEM_PROMPT
        if messages[0]["role"] == "system":
            sys_message = messages[0]["content"]
            messages = messages[1:]

        for i, message in enumerate(messages):
            # The message history MUST lead with a user message
            # and then alternate between user and assistant
            if (message["role"] == "user") != (i % 2 == 0):
                raise Exception("Conversation roles must alternate user/assistant/user/assistant/...")

            # Remove any leading or trailing whitespace characters
            message["content"] = message["content"].strip()

            # Check for empty messages
            if not message["content"]:
                raise ValueError("Messages can't be empty!")

            # Format the message history into a single string
            if message["role"] == "user":
                chat += "[INST]\n" \
                        + (f"<system>\n{sys_message}\n</system>\n\n" if sys_message else "") \
                        + f"{message['content']}\n[/INST]"
            elif message["role"] == "assistant":
                chat += f"{message['content']}{self.tokenizer.eos_token}"
            elif message["role"] == "system":
                raise Exception("System messages must be the first entry in the history.")
            else:
                raise Exception("Only system, user, and assistant roles are supported!")

        return self.tokenizer(chat, return_tensors="pt", return_attention_mask=True)
    
    def prompt(
            self,
            history: list[dict[str, str]] | Conversation,
            prompt: str,
        ) -> str:
        history.append({"role": "user", "content": prompt})
        input_ids: BatchEncoding = self._apply_chat_template(history).to("cuda")

        outputs = self.model.generate(
            **input_ids,
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
        self._history: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]

    _SESSIONS: dict[str, Session] = {}

    @staticmethod
    def create(
        name: str,
        model_name_or_path: str | PathLike,
        max_new_tokens: int,
        system_prompt: str = Model._SYSTEM_PROMPT
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
        self._history[0] = {"role": "system", "content": self._system_prompt}
    
    def prompt(self, prompt: str, ephemeral: bool = False) -> str:
        res: str = self.model.prompt(self._history, prompt)

        # Pop twice to remove the newly added user and assistant messages if ephemeral
        if ephemeral:
            self._history.pop()
            self._history.pop()
        
        return res

    def clear(self) -> None:
        self._history = [{"role": "system", "content": self._system_prompt}]

    @property
    def history(self) -> list[dict[str, str]]:
        return copy.deepcopy(self._history)

    def delete(self) -> None:
        del Session._SESSIONS[self.name]
