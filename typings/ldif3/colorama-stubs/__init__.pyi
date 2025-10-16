import sys
from collections.abc import Callable
from typing import Literal

STDOUT: Literal[-11]
STDERR: Literal[-12]
ENABLE_VIRTUAL_TERMINAL_PROCESSING: int
if sys.platform == "win32": ...
else:
    windll: None
    SetConsoleTextAttribute: Callable[..., None]
    winapi_test: Callable[..., None]
