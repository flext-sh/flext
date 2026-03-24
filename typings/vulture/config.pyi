
from typing import BinaryIO

DEFAULTS: dict[str, t.Scalar | list[str]]

class InputError(Exception):
    message: str
    def __init__(self, message: str) -> None: ...

def make_config(
    argv: list[str] | None = None,
    tomlfile: BinaryIO | None = None,
) -> dict[str, t.Scalar | list[str]]: ...
