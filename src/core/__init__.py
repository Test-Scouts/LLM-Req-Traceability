"""
Core functionality module for REST-at.

Includes:
---------
Classes for abstracting pretrained models and conversation sessions.\n
A function for formatting prompt strings.\n
A class for abstracting REST specifications.\n
A class for calculating and formatting statistical data.
"""
__all__ = [
    "model",
    "prompt",
    "rest",
    "stats"
]


from . import model
from . import prompt
from . import rest
from . import stats
