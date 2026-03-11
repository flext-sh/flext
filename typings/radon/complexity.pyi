
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
    r"""Rank the complexity score from A to F, where A stands for the simplest
    and best score and F the most complex and worst one:

    ============= =====================================================
        1 - 5        A (low risk - simple block)
        6 - 10       B (low risk - well structured and stable block)
        11 - 20      C (moderate risk - slightly complex block)
        21 - 30      D (more than moderate risk - more complex block)
        31 - 40      E (high risk - complex block, alarming)
        41+          F (very high risk - error-prone, unstable block)
    ============= =====================================================

    Here *block* is used in place of function, method or class.

    The formula used to convert the score into an index is the following:

    .. math::

        \text{rank} = \left \lceil \dfrac{\text{score}}{10} \right \rceil
        - H(5 - \text{score})

    where ``H(s)`` stands for the Heaviside Step Function.
    The rank is then associated to a letter (0 = A, 5 = F).
    """
    ...

def average_complexity(blocks: Sequence[Block]) -> float:
    """Compute the average Cyclomatic complexity from the given blocks.
    Blocks must be either :class:`~radon.visitors.Function` or
    :class:`~radon.visitors.Class`. If the block list is empty, then 0 is
    returned.
    """
    ...

def sorted_results(
    blocks: Sequence[Block],
    order: Callable[[Block], SortKey] = ...,
) -> list[Block]:
    """Given a ComplexityVisitor instance, returns a list of sorted blocks
    with respect to complexity. A block is a either
    :class:`~radon.visitors.Function` object or a
    :class:`~radon.visitors.Class` object.
    The blocks are sorted in descending order from the block with the highest
    complexity.

    The optional `order` parameter indicates how to sort the blocks. It can be:

        * `LINES`: sort by line numbering;
        * `ALPHA`: sort by name (from A to Z);
        * `SCORE`: sorty by score (descending).

    Default is `SCORE`.
    """
    ...

def add_inner_blocks(blocks: Sequence[Block]) -> list[Block]:
    """Process a list of blocks by adding all closures and inner classes as
    top-level blocks.
    """
    ...

def cc_visit(code: str, **kwargs: bool | str | None) -> list[Block]:
    """Visit the given code with :class:`~radon.visitors.ComplexityVisitor`.
    All the keyword arguments are directly passed to the visitor.
    """
    ...

def cc_visit_ast(
    ast_node: ast.AST,
    **kwargs: bool | str | None,
) -> list[Block]:
    """Visit the AST node with :class:`~radon.visitors.ComplexityVisitor`. All
    the keyword arguments are directly passed to the visitor.
    """
    ...
