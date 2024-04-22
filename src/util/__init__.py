"""
Utility module for REST-at.

Includes:
---------
Classes for abstracting pretrained models and conversation sessions.\n
A function for formatting prompt strings.\n
A class for abstragting REST specifications.
"""
__all__ = [
    "model",
    "prompt",
    "rest"
]


from . import model
from . import prompt
from . import rest
