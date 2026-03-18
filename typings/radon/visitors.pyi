import ast
from collections.abc import Callable, Iterable
from typing import NamedTuple, Self, override

"""This module contains the ComplexityVisitor class which is where all the
analysis concerning Cyclomatic Complexity is done. There is also the class
HalsteadVisitor, that counts Halstead metrics."""

GET_COMPLEXITY: Callable[[Function], int]
GET_REAL_COMPLEXITY: Callable[[Class], int]
NAMES_GETTER: Callable[[ast.alias], tuple[str, str | None]]
GET_ENDLINE: Callable[[Function], int]

class BaseFunc(NamedTuple):
    name: str
    lineno: int
    col_offset: int
    endline: int
    is_method: bool
    classname: str | None
    closures: list[Function]
    complexity: int

class BaseClass(NamedTuple):
    name: str
    lineno: int
    col_offset: int
    endline: int
    methods: list[Function]
    inner_classes: list[Class]
    real_complexity: int

type HalsteadDispatchResult = tuple[
    int,
    int,
    Iterable[str],
    Iterable[ast.expr | ast.operator],
]

def code2ast(source: str) -> ast.Module: ...

class Function(BaseFunc):
    @property
    def letter(self) -> str: ...
    @property
    def fullname(self) -> str: ...

class Class(BaseClass):
    letter: str

    @property
    def fullname(self) -> str: ...
    @property
    def complexity(self) -> int: ...

class CodeVisitor(ast.NodeVisitor):
    @staticmethod
    def get_name(obj: object) -> str: ...
    @classmethod
    def from_code(cls, code: str, **kwargs: object) -> Self: ...
    @classmethod
    def from_ast(cls, ast_node: ast.AST, **kwargs: object) -> Self: ...
    @override
    def visit_Constant(self, node: ast.Constant) -> None: ...

class ComplexityVisitor(CodeVisitor):
    off: bool
    complexity: int
    functions: list[Function]
    classes: list[Class]
    to_method: bool
    classname: str | None
    no_assert: bool

    def __init__(
        self,
        to_method: bool = ...,
        classname: str | None = ...,
        off: bool = ...,
        no_assert: bool = ...,
    ) -> None: ...
    @property
    def functions_complexity(self) -> int: ...
    @property
    def classes_complexity(self) -> int: ...
    @property
    def total_complexity(self) -> int: ...
    @property
    def blocks(self) -> list[Function | Class]: ...
    @property
    def max_line(self) -> float: ...
    @max_line.setter
    def max_line(self, value: float) -> None: ...
    @override
    def generic_visit(self, node: ast.AST) -> None: ...
    @override
    def visit_Assert(self, node: ast.Assert) -> None: ...
    @override
    def visit_Constant(self, node: ast.Constant) -> None: ...
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None: ...
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None: ...
    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None: ...

class HalsteadVisitor(CodeVisitor):
    types: dict[str, str]
    operators_seen: set[tuple[str | None, str]]
    operands_seen: set[tuple[str | None, object]]
    operators: int
    operands: int
    context: str | None
    function_visitors: list[HalsteadVisitor]

    def __init__(self, context: str | None = ...) -> None: ...
    @property
    def distinct_operators(self) -> int: ...
    @property
    def distinct_operands(self) -> int: ...
    @staticmethod
    def dispatch(
        meth: Callable[..., object],
    ) -> Callable[..., None]: ...
    @override
    def visit_BinOp(
        self,
        node: ast.BinOp,
    ) -> tuple[int, int, tuple[str], tuple[ast.expr, ast.expr]]: ...
    @override
    def visit_UnaryOp(
        self,
        node: ast.UnaryOp,
    ) -> tuple[int, int, tuple[str], tuple[ast.expr]]: ...
    @override
    def visit_BoolOp(
        self,
        node: ast.BoolOp,
    ) -> tuple[int, int, tuple[str], list[ast.expr]]: ...
    @override
    def visit_AugAssign(
        self,
        node: ast.AugAssign,
    ) -> tuple[int, int, tuple[str], tuple[ast.expr, ast.expr]]: ...
    @override
    def visit_Compare(
        self,
        node: ast.Compare,
    ) -> tuple[int, int, Iterable[str], list[ast.expr]]: ...
    @override
    def visit_Constant(self, node: ast.Constant) -> None: ...
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None: ...
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None: ...
