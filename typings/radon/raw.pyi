"""Type stubs for radon.raw module."""

from collections.abc import Callable, Generator, Iterable, Iterator, Sequence
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

def _generate(code: str) -> list[TokenInfo]:
    """Pass the code into `tokenize.generate_tokens` and convert the result
    into a list.
    """
    ...

def _fewer_tokens(
    tokens: Iterable[TokenInfo],
    remove: Iterable[int],
) -> Generator[TokenInfo]:
    """Process the output of `tokenize.generate_tokens` removing
    the tokens specified in `remove`.
    """
    ...

def _find(tokens: Sequence[TokenInfo], token: int, value: str) -> int:
    """Return the position of the last token with the same (token, value)
    pair supplied. The position is the one of the rightmost term.
    """
    ...

def _split_tokens(
    tokens: Sequence[TokenInfo],
    token: int,
    value: str,
) -> list[list[TokenInfo]]:
    """Split a list of tokens on the specified token pair (token, value),
    where *token* is the token type (i.e. its code) and *value* its actual
    value in the code.
    """
    ...

def _get_all_tokens(
    line: str,
    lines: Iterator[str],
) -> tuple[list[TokenInfo], list[str]]:
    """Starting from *line*, generate the necessary tokens which represent the
    shortest tokenization possible. This is done by catching
    :exc:`tokenize.TokenError` when a multi-line string or statement is
    encountered.
    :returns: tokens, lines
    """
    ...

def _logical(tokens: Sequence[TokenInfo]) -> int:
    """Find how many logical lines are there in the current line.

    Normally 1 line of code is equivalent to 1 logical line of code,
    but there are cases when this is not true. For example::

        if cond:
            return 0

    this line actually corresponds to 2 logical lines, since it can be
    translated into::

        if cond:
            return 0

    Examples::

        if cond:  -> 1

        if cond: return 0  -> 2

        try: 1/0  -> 2

        try:  -> 1

        if cond:  # Only a comment  -> 1

        if cond: return 0  # Only a comment  -> 2
    """
    ...

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
