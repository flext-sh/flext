"""Type stubs for vulture.reachability module."""

from __future__ import annotations

import ast
from collections.abc import Callable

class Reachability:
    def __init__(self, report: Callable[..., None]) -> None: ...
    def visit(self, node: ast.AST) -> None: ...
    def reset(self) -> None: ...
