
import ast
from collections.abc import Callable, Sequence
from typing import TypeAlias

from radon.visitors import Class, Function

"""This module contains all high-level helpers function that allow to work with
Cyclomatic Complexity
"""

Block: TypeAlias = Function | Class
SortKey: TypeAlias = int | float | str

SCORE: Callable[[Block], SortKey]
LINES: Callable[[Block], SortKey]
ALPHA: Callable[[Block], SortKey]

def cc_rank(cc: float) -> str:
    
    ...

def average_complexity(blocks: Sequence[Block]) -> float:
    
    ...

def sorted_results(
    blocks: Sequence[Block],
    order: Callable[[Block], SortKey] = ...,
) -> list[Block]:
    
    ...

def add_inner_blocks(blocks: Sequence[Block]) -> list[Block]:
    
    ...

def cc_visit(code: str, **kwargs: bool | str | None) -> list[Block]:
    
    ...

def cc_visit_ast(
    ast_node: ast.AST,
    **kwargs: bool | str | None,
) -> list[Block]:
    
    ...
