"""Type stubs for radon.raw module."""

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
    """Is this a single token matching token_number followed by ENDMARKER, NL
    or NEWLINE tokens.
    """
    ...

def analyze(source: str) -> Module:
    """Analyze the source code and return a namedtuple with the following
    fields:

        * **loc**: The number of lines of code (total)
        * **lloc**: The number of logical lines of code
        * **sloc**: The number of source lines of code (not necessarily
            corresponding to the LLOC)
        * **comments**: The number of Python comment lines
        * **multi**: The number of lines which represent multi-line strings
        * **single_comments**: The number of lines which are just comments with
            no code
        * **blank**: The number of blank lines (or whitespace-only ones)

    The equation :math:`sloc + blanks + multi + single_comments = loc` should
    always hold.  Multiline strings are not counted as comments, since, to the
    Python interpreter, they are not comments but strings.
    """
    ...
