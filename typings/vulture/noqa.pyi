"""Type stubs for vulture.noqa module."""

from __future__ import annotations

import re
from collections import defaultdict

NOQA_REGEXP: re.Pattern[str]
NOQA_CODE_MAP: dict[str, str]

def parse_noqa(code: list[str]) -> defaultdict[str, set[int]]: ...
def ignore_line(
    noqa_lines: defaultdict[str, set[int]],
    lineno: int,
    error_code: str,
) -> bool: ...
