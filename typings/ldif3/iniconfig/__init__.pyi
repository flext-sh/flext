from typing import NamedTuple

COMMENTCHARS = ...

class _ParsedLine(NamedTuple):
    lineno: int
    section: str | None
    name: str | None
    value: str | None

def parse_lines(path: str, line_iter: list[str]) -> list[_ParsedLine]: ...
def iscommentline(line: str) -> bool: ...
