"""Type stubs for ruff._find_ruff module."""

from __future__ import annotations

class RuffNotFound(FileNotFoundError): ...

def find_ruff_bin() -> str: ...
