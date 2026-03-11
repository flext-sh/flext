"""Type stubs for vulture.config module."""

from __future__ import annotations

from typing import BinaryIO

DEFAULTS: dict[str, str | int | bool | list[str]]

class InputError(Exception):
    message: str
    def __init__(self, message: str) -> None: ...

def make_config(
    argv: list[str] | None = None,
    tomlfile: BinaryIO | None = None,
) -> dict[str, str | int | bool | list[str]]: ...
