#!/usr/bin/env python3
from __future__ import annotations

"""Final comprehensive docstring gap scanner for FLX project."""

import ast
import os
from typing import Any


class DocstringGapFinder(ast.NodeVisitor):
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.gaps: list[dict[str, Any]] = []
        self.current_class = None

    def has_docstring(self, node: ast.AST) -> bool:
        return (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self.current_class
        self.current_class = node.name

        if not self.has_docstring(node):
            self.gaps.append(
                {
                    "file": self.filepath,
                    "line": node.lineno,
                    "type": "class",
                    "name": node.name,
                    "description": f"Class {node.name}",
                }
            )

        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if not self.has_docstring(node):
            func_type = "method" if self.current_class else "function"
            name = node.name

            # Skip private methods except __init__
            if name.startswith("_") and name != "__init__":
                if not name.startswith("__") or name in {
                    "__enter__",
                    "__exit__",
                    "__call__",
                }:
                    self.generic_visit(node)
                    return

            self.gaps.append(
                {
                    "file": self.filepath,
                    "line": node.lineno,
                    "type": func_type,
                    "name": name,
                    "description": f"{func_type} {name}",
                }
            )

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if not self.has_docstring(node):
            func_type = "async_method" if self.current_class else "async_function"
            name = node.name

            # Skip private methods except __init__
            if name.startswith("_") and name != "__init__":
                if not name.startswith("__") or name in {
                    "__aenter__",
                    "__aexit__",
                    "__call__",
                }:
                    self.generic_visit(node)
                    return

            self.gaps.append(
                {
                    "file": self.filepath,
                    "line": node.lineno,
                    "type": func_type,
                    "name": name,
                    "description": f"{func_type} {name}",
                }
            )

        self.generic_visit(node)


def scan_file(filepath: str) -> list[dict[str, Any]]:
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        if not content.strip():
            return []

        tree = ast.parse(content, filename=filepath)
        finder = DocstringGapFinder(filepath)
        finder.visit(tree)
        return finder.gaps

    except Exception:
        return []


def scan_directory(directory: str) -> list[dict[str, Any]]:
    all_gaps = []

    for root, _dirs, files in os.walk(directory):
        if "test" in root or "__pycache__" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                gaps = scan_file(filepath)
                all_gaps.extend(gaps)

    return all_gaps


def main():
    flx_dir = "/home/marlonsc/pyauto/flx/src/flx"

    gaps = scan_directory(flx_dir)

    if gaps:
        gaps_by_file = {}
        for gap in gaps:
            file_path = gap["file"]
            if file_path not in gaps_by_file:
                gaps_by_file[file_path] = []
            gaps_by_file[file_path].append(gap)

        for file_path, file_gaps in sorted(
            gaps_by_file.items(), key=lambda x: len(x[1]), reverse=True
        ):
            file_path.replace("/home/marlonsc/pyauto/flx/", "")

            for gap in sorted(file_gaps, key=lambda x: x["line"]):
                pass

    return gaps


if __name__ == "__main__":
    main()
