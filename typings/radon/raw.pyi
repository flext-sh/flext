

from collections.abc import Callable, Sequence
from typing import NamedTuple

"""This module contains functions related to raw metrics.

The main function is :func:`~radon.raw.analyze`, and should be the only one
that is used.
"""

COMMENT: int
OP: int
TOKEN_NUMBER: Callable[[TokenInfo], int]
NL: int
NEWLINE: int
EM: int

type TokenInfo = tuple[int, str, tuple[int, int], tuple[int, int], str]

class Module(NamedTuple):
    loc: int
    lloc: int
    sloc: int
    comments: int
    multi: int
    blank: int
    single_comments: int

def is_single_token(token_number: int, tokens: Sequence[TokenInfo]) -> bool:
    
    ...

def analyze(source: str) -> Module:
    
    ...
