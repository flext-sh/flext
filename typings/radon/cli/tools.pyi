"""Type stubs for radon.cli.tools module."""

from collections.abc import Generator, Iterable

from radon.visitors import Class, Function

"""This module contains various utility functions used in the CLI interface.
Attributes:
    _encoding (str): encoding with all files will be opened. Configured by
    environment variable RADONFILESENCODING
"""

SUPPORTS_IPYNB: bool
BRIGHT: str
LETTERS_COLORS: dict[str, str]
RANKS_COLORS: dict[str, str]
RESET: str
TEMPLATE: str
default_encoding: str

def iter_filenames(
    paths: Iterable[str],
    exclude: str | None = ...,
    ignore: str | None = ...,
) -> Generator[str]:
    """A generator that yields all sub-paths of the ones specified in
    `paths`. Optional `exclude` filters can be passed as a comma-separated
    string of regexes, while `ignore` filters are a comma-separated list of
    directory names to ignore. Ignore patterns are can be plain names or glob
    patterns. If paths contains only a single hyphen, stdin is implied,
    returned as is.
    """
    ...

def explore_directories(
    start: str,
    exclude: Iterable[str],
    ignore: Iterable[str],
) -> Generator[str]:
    """Explore files and directories under `start`. `explore` and `ignore`
    arguments are the same as in :func:`iter_filenames`.
    """
    ...

def filter_out(strings: Iterable[str], patterns: Iterable[str]) -> Generator[str]:
    """Filter out any string that matches any of the specified patterns."""
    ...

def cc_to_dict(obj: Function | Class) -> dict[str, object]:
    """Convert an object holding CC results into a dictionary. This is meant
    for JSON dumping.
    """
    ...

def raw_to_dict(obj: object) -> dict[str, int]:
    """Convert an object holding raw analysis results into a dictionary. This
    is meant for JSON dumping.
    """
    ...

def dict_to_xml(results: dict[str, list[dict[str, object]]]) -> str:
    """Convert a dictionary holding CC analysis result into a string containing
    xml.
    """
    ...

def dict_to_md(results: dict[str, list[dict[str, object]]]) -> str: ...
def dict_to_codeclimate_issues(
    results: dict[str, object],
    threshold: str = ...,
) -> list[str]:
    """Convert a dictionary holding CC analysis results into Code Climate
    issue json.
    """
    ...

def cc_to_terminal(
    results: Iterable[Function | Class],
    show_complexity: bool,
    min: str,
    max: str,
    total_average: bool,
) -> tuple[list[str], float, int]:
    """Transfom Cyclomatic Complexity results into a 3-elements tuple:

        ``(res, total_cc, counted)``

    `res` is a list holding strings that are specifically formatted to be
    printed to a terminal.
    `total_cc` is a number representing the total analyzed cyclomatic
    complexity.
    `counted` holds the number of the analyzed blocks.

    If *show_complexity* is `True`, then the complexity of a block will be
    shown in the terminal line alongside its rank.
    *min* and *max* are used to control which blocks are shown in the resulting
    list. A block is formatted only if its rank is `min <= rank <= max`.
    If *total_average* is `True`, the `total_cc` and `counted` count every
    block, regardless of the fact that they are formatted in `res` or not.
    """
    ...

def _format_line(
    block: Function | Class, ranked: str, show_complexity: bool = ...
) -> str:
    """Format a single block as a line.

    *ranked* is the rank given by the `~radon.complexity.rank` function. If
    *show_complexity* is True, then the complexity score is added alongside.
    """
    ...

def format_cc_issue(
    path: str,
    description: str,
    content: str,
    category: str,
    beginline: int,
    endline: int,
    remediation_points: int,
    fingerprint: str,
) -> str:
    """Return properly formatted Code Climate issue json."""
    ...

def get_remediation_points(complexity: int, grade_threshold: str) -> int:
    """Calculate quantity of remediation work needed to reduce complexity to grade
    threshold permitted.
    """
    ...

def get_content() -> str:
    """Return explanation string for Code Climate issue document."""
    ...

def get_fingerprint(path: str, additional_parts: list[str]) -> str:
    """Return fingerprint string for Code Climate issue document."""
    ...

def strip_ipython(code: str) -> str: ...
