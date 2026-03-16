
import ast
from typing import NamedTuple

from radon.visitors import HalsteadVisitor

"""Module holding functions related to miscellaneous metrics, such as Halstead
metrics or the Maintainability Index.
"""

class HalsteadReport(NamedTuple):
    h1: int
    h2: int
    N1: int
    N2: int
    vocabulary: int
    length: int
    calculated_length: float
    volume: float
    difficulty: float
    effort: float
    time: float
    bugs: float

class Halstead(NamedTuple):
    total: HalsteadReport
    functions: list[tuple[str, HalsteadReport]]

def h_visit(code: str) -> Halstead:
    
    ...

def h_visit_ast(ast_node: ast.AST) -> Halstead:
    
    ...

def halstead_visitor_report(visitor: HalsteadVisitor) -> HalsteadReport:
    
    ...

def mi_compute(
    halstead_volume: float,
    complexity: float,
    sloc: float,
    comments: float,
) -> float:
    
    ...

def mi_parameters(code: str, count_multi: bool = ...) -> tuple[float, int, int, float]:
    
    ...

def mi_visit(code: str, multi: bool) -> float:
    
    ...

def mi_rank(score: float) -> str:
    
    ...
