import ast
from collections import defaultdict
from pathlib import Path
from typing import override

from vulture.reachability import Reachability
from vulture.utils import ExitCode, LoggingList, LoggingSet

DEFAULT_CONFIDENCE: int
IGNORED_VARIABLE_NAMES: set[str]
PYTEST_FUNCTION_NAMES: set[str]
PYTEST_METHOD_NAMES: set[str]
ERROR_CODES: dict[str, str]

class Item:
    __slots__: tuple[str, ...]
    name: str
    typ: str
    filename: Path
    first_lineno: int
    last_lineno: int
    message: str
    confidence: int

    def __init__(
        self,
        name: str,
        typ: str,
        filename: Path,
        first_lineno: int,
        last_lineno: int,
        message: str = "",
        confidence: int = ...,
    ) -> None: ...
    @property
    def size(self) -> int: ...
    def get_report(self, add_size: bool = False) -> str: ...
    def get_whitelist_string(self) -> str: ...
    @override
    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...

class Vulture(ast.NodeVisitor):
    verbose: bool
    defined_attrs: LoggingList
    defined_classes: LoggingList
    defined_funcs: LoggingList
    defined_imports: LoggingList
    defined_methods: LoggingList
    defined_props: LoggingList
    defined_vars: LoggingList
    unreachable_code: LoggingList
    used_names: LoggingSet
    ignore_names: list[str]
    ignore_decorators: list[str]
    filename: Path
    code: list[str]
    exit_code: ExitCode
    noqa_lines: defaultdict[str, set[int]] | dict[str, set[int]]
    reachability: Reachability

    def __init__(
        self,
        verbose: bool = False,
        ignore_names: list[str] | None = None,
        ignore_decorators: list[str] | None = None,
    ) -> None: ...
    def scan(self, code: str, filename: str = "") -> None: ...
    def scavenge(
        self,
        paths: list[str] | list[Path],
        exclude: list[str] | None = None,
    ) -> None: ...
    def get_unused_code(
        self,
        min_confidence: int = 0,
        sort_by_size: bool = False,
    ) -> list[Item]: ...
    def report(
        self,
        min_confidence: int = 0,
        sort_by_size: bool = False,
        make_whitelist: bool = False,
    ) -> ExitCode: ...
    @property
    def unused_classes(self) -> list[Item]: ...
    @property
    def unused_funcs(self) -> list[Item]: ...
    @property
    def unused_imports(self) -> list[Item]: ...
    @property
    def unused_methods(self) -> list[Item]: ...
    @property
    def unused_props(self) -> list[Item]: ...
    @property
    def unused_vars(self) -> list[Item]: ...
    @property
    def unused_attrs(self) -> list[Item]: ...
    @override
    def visit_arg(self, node: ast.arg) -> None: ...
    @override
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None: ...
    @override
    def visit_Attribute(self, node: ast.Attribute) -> None: ...
    @override
    def visit_BinOp(self, node: ast.BinOp) -> None: ...
    @override
    def visit_Call(self, node: ast.Call) -> None: ...
    @override
    def visit_ClassDef(self, node: ast.ClassDef) -> None: ...
    @override
    def visit_Constant(self, node: ast.Constant) -> None: ...
    @override
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None: ...
    @override
    def visit_Import(self, node: ast.Import) -> None: ...
    @override
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None: ...
    @override
    def visit_Name(self, node: ast.Name) -> None: ...
    @override
    def visit_Assign(self, node: ast.Assign) -> None: ...
    @override
    def visit_MatchClass(self, node: ast.MatchClass) -> None: ...
    @override
    def visit(self, node: ast.AST) -> None: ...
    @override
    def generic_visit(self, node: ast.AST) -> None: ...

def main() -> None: ...
