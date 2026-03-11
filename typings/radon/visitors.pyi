"""Type stubs for radon.visitors module."""

from __future__ import annotations

import ast
from collections.abc import Callable, Iterable
from typing import NamedTuple, Self

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

def code2ast(source: str) -> ast.Module:
    """Convert a string object into an AST object.

    This function is retained for backwards compatibility, but it no longer
    attemps any conversions. It's equivalent to a call to ``ast.parse``.
    """
    ...

class Function(BaseFunc):
    """Object represeting a function block."""

    @property
    def letter(self) -> str:
        """The letter representing the function. It is `M` if the function is
        actually a method, `F` otherwise.
        """
        ...

    @property
    def fullname(self) -> str:
        """The full name of the function. If it is a method, then the full name
        is:
                {class name}.{method name}
        Otherwise it is just the function name.
        """
        ...

class Class(BaseClass):
    """Object representing a class block."""

    letter: str

    @property
    def fullname(self) -> str:
        """The full name of the class. It is just its name. This attribute
        exists for consistency (see :data:`Function.fullname`).
        """
        ...

    @property
    def complexity(self) -> int:
        """The average complexity of the class. It corresponds to the average
        complexity of its methods plus one.
        """
        ...

class CodeVisitor(ast.NodeVisitor):
    """Base class for every NodeVisitors in `radon.visitors`. It implements a
    couple utility class methods and a static method.
    """

    @staticmethod
    def get_name(obj: object) -> str:
        """Shorthand for ``obj.__class__.__name__``."""
        ...

    @classmethod
    def from_code(cls, code: str, **kwargs: object) -> Self:
        """Instanciate the class from source code (string object). The
        `**kwargs` are directly passed to the `ast.NodeVisitor` constructor.
        """
        ...

    @classmethod
    def from_ast(cls, ast_node: ast.AST, **kwargs: object) -> Self:
        """Instantiate the class from an AST node. The `**kwargs` are
        directly passed to the `ast.NodeVisitor` constructor.
        """
        ...

    def visit_Constant(self, node: ast.Constant) -> None: ...

class ComplexityVisitor(CodeVisitor):
    """A visitor that keeps track of the cyclomatic complexity of
    the elements.

    :param to_method: If True, every function is treated as a method. In this
        case the *classname* parameter is used as class name.
    :param classname: Name of parent class.
    :param off: If True, the starting value for the complexity is set to 1,
        otherwise to 0.
    """

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
    def functions_complexity(self) -> int:
        """The total complexity from all functions (i.e. the total number of
        decision points + 1).

        This is *not* the sum of all the complexity from the functions. Rather,
        it's the complexity of the code *inside* all the functions.
        """
        ...

    @property
    def classes_complexity(self) -> int:
        """The total complexity from all classes (i.e. the total number of
        decision points + 1).
        """
        ...

    @property
    def total_complexity(self) -> int:
        """The total complexity. Computed adding up the visitor complexity, the
        functions complexity, and the classes complexity.
        """
        ...

    @property
    def blocks(self) -> list[Function | Class]:
        """All the blocks visited. These include: all the functions, the
        classes and their methods. The returned list is not sorted.
        """
        ...

    @property
    def max_line(self) -> float:
        """The maximum line number among the analyzed lines."""
        ...

    @max_line.setter
    def max_line(self, value: float) -> None:
        """The maximum line number among the analyzed lines."""
        ...

    def generic_visit(self, node: ast.AST) -> None:
        """Main entry point for the visitor."""
        ...

    def visit_Assert(self, node: ast.Assert) -> None:
        """When visiting `assert` statements, the complexity is increased only
        if the `no_assert` attribute is `False`.
        """
        ...

    def visit_Constant(self, node: ast.Constant) -> None: ...
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Async function definition is the same thing as the synchronous
        one.
        """
        ...

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """When visiting functions a new visitor is created to recursively
        analyze the function's body.
        """
        ...

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """When visiting classes a new visitor is created to recursively
        analyze the class' body and methods.
        """
        ...

class HalsteadVisitor(CodeVisitor):
    """Visitor that keeps track of operators and operands, in order to compute
    Halstead metrics (see :func:`radon.metrics.h_visit`).
    """

    types: dict[str, str]
    operators_seen: set[tuple[str | None, str]]
    operands_seen: set[tuple[str | None, object]]
    operators: int
    operands: int
    context: str | None
    function_visitors: list[HalsteadVisitor]

    def __init__(self, context: str | None = ...) -> None:
        """*context* is a string used to keep track the analysis' context."""
        ...

    @property
    def distinct_operators(self) -> int:
        """The number of distinct operators."""
        ...

    @property
    def distinct_operands(self) -> int:
        """The number of distinct operands."""
        ...

    @staticmethod
    def dispatch(
        meth: Callable[..., object],
    ) -> Callable[..., None]:
        """This decorator does all the hard work needed for every node.

        The decorated method must return a tuple of 4 elements:

            * the number of operators
            * the number of operands
            * the operators seen (a sequence)
            * the operands seen (a sequence)
        """
        ...

    def visit_BinOp(
        self,
        node: ast.BinOp,
    ) -> tuple[int, int, tuple[str], tuple[ast.expr, ast.expr]]:
        """A binary operator."""
        ...

    def visit_UnaryOp(
        self,
        node: ast.UnaryOp,
    ) -> tuple[int, int, tuple[str], tuple[ast.expr]]:
        """A unary operator."""
        ...

    def visit_BoolOp(
        self,
        node: ast.BoolOp,
    ) -> tuple[int, int, tuple[str], list[ast.expr]]:
        """A boolean operator."""
        ...

    def visit_AugAssign(
        self,
        node: ast.AugAssign,
    ) -> tuple[int, int, tuple[str], tuple[ast.expr, ast.expr]]:
        """An augmented assign (contains an operator)."""
        ...

    def visit_Compare(
        self,
        node: ast.Compare,
    ) -> tuple[int, int, Iterable[str], list[ast.expr]]:
        """A comparison."""
        ...

    def visit_Constant(self, node: ast.Constant) -> None: ...
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """When visiting functions, another visitor is created to recursively
        analyze the function's body. We also track information on the function
        itself.
        """
        ...

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Async functions are similar to standard functions, so treat them as
        such.
        """
        ...
