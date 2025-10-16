import ast
from collections.abc import Callable, Collection
from typing import Any, NamedTuple, TypeVar

"""Tools for understanding predicates, to satisfy them by construction.

For example::

    integers().filter(lambda x: x >= 0) -> integers(min_value=0)

This is intractable in general, but reasonably easy for simple cases involving
numeric bounds, strings with length or regex constraints, and collection lengths -
and those are precisely the most common cases.  When they arise in e.g. Pandas
dataframes, it's also pretty painful to do the constructive version by hand in
a library; so we prefer to share all the implementation effort here.
See https://github.com/HypothesisWorks/hypothesis/issues/2701 for details.
"""
Ex = TypeVar("Ex")
type Predicate[Ex] = Callable[[Ex], bool]

class ConstructivePredicate(NamedTuple):
    constraints: dict[str, Any]
    predicate: Predicate | None
    @classmethod
    def unchanged(cls, predicate: Predicate) -> ConstructivePredicate: ...

ARG = ...

def convert(node: ast.AST, argname: str) -> object: ...
def comp_to_constraints(
    x: ast.AST, op: ast.AST, y: ast.AST, *, argname: str
) -> dict: ...
def merge_preds(*con_predicates: ConstructivePredicate) -> ConstructivePredicate: ...
def numeric_bounds_from_ast(
    tree: ast.AST, argname: str, fallback: ConstructivePredicate
) -> ConstructivePredicate: ...
def get_numeric_predicate_bounds(predicate: Predicate) -> ConstructivePredicate: ...
def get_integer_predicate_bounds(predicate: Predicate) -> ConstructivePredicate: ...
def get_float_predicate_bounds(predicate: Predicate) -> ConstructivePredicate: ...
def max_len(size: int, element: Collection[object]) -> bool: ...
def min_len(size: int, element: Collection[object]) -> bool: ...
