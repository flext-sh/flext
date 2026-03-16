

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
    
    ...

def explore_directories(
    start: str,
    exclude: Iterable[str],
    ignore: Iterable[str],
) -> Generator[str]:
    
    ...

def filter_out(strings: Iterable[str], patterns: Iterable[str]) -> Generator[str]:
    
    ...

def cc_to_dict(obj: Function | Class) -> dict[str, object]:
    
    ...

def raw_to_dict(obj: object) -> dict[str, int]:
    
    ...

def dict_to_xml(results: dict[str, list[dict[str, object]]]) -> str:
    
    ...

def dict_to_md(results: dict[str, list[dict[str, object]]]) -> str: ...
def dict_to_codeclimate_issues(
    results: dict[str, object],
    threshold: str = ...,
) -> list[str]:
    
    ...

def cc_to_terminal(
    results: Iterable[Function | Class],
    show_complexity: bool,
    min: str,
    max: str,
    total_average: bool,
) -> tuple[list[str], float, int]:
    
    ...

def _format_line(
    block: Function | Class, ranked: str, show_complexity: bool = ...
) -> str:
    
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
    
    ...

def get_remediation_points(complexity: int, grade_threshold: str) -> int:
    
    ...

def get_content() -> str:
    
    ...

def get_fingerprint(path: str, additional_parts: list[str]) -> str:
    
    ...

def strip_ipython(code: str) -> str: ...
