"""Type stubs for vulture.lines module."""

from __future__ import annotations

import ast

def get_last_line_number(node: ast.AST) -> int: ...
def get_first_line_number(node: ast.AST) -> int: ...
