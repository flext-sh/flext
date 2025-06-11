#!/usr/bin/env python3
from __future__ import annotations

"""Comprehensive docstring gap scanner for FLX project.
Finds all classes, functions, and methods missing docstrings.
"""

import ast
import os
from typing import Any


class DocstringGapFinder(ast.NodeVisitor):
    """AST visitor to find missing docstrings."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.gaps: list[dict[str, Any]] = []
        self.current_class = None

    def has_docstring(self, node: ast.AST) -> bool:
        """Check if a node has a docstring."""
        # Check if node has body attribute (ClassDef, FunctionDef, AsyncFunctionDef, Module)
        if not hasattr(node, "body") or not node.body:  # type: ignore
            return False

        return (
            node.body  # type: ignore
            and isinstance(node.body[0], ast.Expr)  # type: ignore
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        old_class = self.current_class
        self.current_class = node.name

        if not self.has_docstring(node):
            self.gaps.append(
                {
                    "file": self.filepath,
                    "line": node.lineno,
                    "type": "class",
                    "name": node.name,
                    "parent_class": old_class,
                    "description": f"Class {node.name}",
                }
            )

        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        if not self.has_docstring(node):
            func_type = "method" if self.current_class else "function"
            name = node.name

            # Skip some common patterns that don't need docstrings
            if name.startswith("_") and name != "__init__":
                # Skip private methods except __init__
                if not name.startswith("__") or name in {
                    "__enter__",
                    "__exit__",
                    "__call__",
                }:
                    self.generic_visit(node)
                    return

            description = self._get_function_description(node, func_type)

            self.gaps.append(
                {
                    "file": self.filepath,
                    "line": node.lineno,
                    "type": func_type,
                    "name": name,
                    "parent_class": self.current_class,
                    "description": description,
                }
            )

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        if not self.has_docstring(node):
            func_type = "async_method" if self.current_class else "async_function"
            name = node.name

            # Skip some common patterns
            if name.startswith("_") and name != "__init__":
                if not name.startswith("__") or name in {
                    "__aenter__",
                    "__aexit__",
                    "__call__",
                }:
                    self.generic_visit(node)
                    return

            description = self._get_function_description(node, func_type)

            self.gaps.append(
                {
                    "file": self.filepath,
                    "line": node.lineno,
                    "type": func_type,
                    "name": name,
                    "parent_class": self.current_class,
                    "description": description,
                }
            )

        self.generic_visit(node)

    def _get_function_description(self, node: ast.FunctionDef, func_type: str) -> str:
        """Generate description based on function characteristics."""
        name = node.name

        # Special cases
        if name == "__init__":
            return (
                f"Constructor for {self.current_class}"
                if self.current_class
                else "Constructor"
            )

        if name.startswith("__") and name.endswith("__"):
            return f"Magic method {name}"

        if name.startswith("test_"):
            return f'Test {name.replace("test_", "").replace("_", " ")}'

        if name.startswith("_"):
            return f"Private {func_type} {name}"

        # Check for common patterns
        if name.startswith("get_"):
            return f'Get {name[4:].replace("_", " ")}'

        if name.startswith("set_"):
            return f'Set {name[4:].replace("_", " ")}'

        if name.startswith(("is_", "has_")):
            return f'Check if {name[3:].replace("_", " ") if name.startswith("is_") else name[4:].replace("_", " ")}'

        if name in {"connect", "disconnect", "close", "open"}:
            return f"{name.capitalize()} connection"

        if name in {"start", "stop", "pause", "resume"}:
            return f"{name.capitalize()} operation"

        if name.endswith("_handler"):
            return f'Handle {name[:-8].replace("_", " ")}'

        if name.endswith("_callback"):
            return f'Callback for {name[:-9].replace("_", " ")}'

        # Default description
        return f'{func_type.capitalize()} {name.replace("_", " ")}'


def scan_file(filepath: str) -> list[dict[str, Any]]:
    """Scan a single file for docstring gaps."""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        # Skip empty files
        if not content.strip():
            return []

        tree = ast.parse(content, filename=filepath)
        finder = DocstringGapFinder(filepath)
        finder.visit(tree)
        return finder.gaps

    except Exception:
        return []


def scan_directory(directory: str) -> list[dict[str, Any]]:
    """Scan all Python files in a directory for docstring gaps."""
    all_gaps = []

    for root, dirs, files in os.walk(directory):
        # Skip test directories for now - focus on main code
        if "test" in root or "__pycache__" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                gaps = scan_file(filepath)
                all_gaps.extend(gaps)

    return all_gaps


def main():
    """Main function to scan FLX project."""
    flx_dir = "/home/marlonsc/pyauto/flx/src/flx"

    gaps = scan_directory(flx_dir)

    # Group by file
    gaps_by_file = {}
    for gap in gaps:
        file_path = gap["file"]
        if file_path not in gaps_by_file:
            gaps_by_file[file_path] = []
        gaps_by_file[file_path].append(gap)

    # Sort files by number of gaps (descending)
    sorted_files = sorted(gaps_by_file.items(), key=lambda x: len(x[1]), reverse=True)

    for file_path, file_gaps in sorted_files[:10]:
        file_path.replace("/home/marlonsc/pyauto/flx/", "")

    for file_path, file_gaps in sorted_files:
        file_path.replace("/home/marlonsc/pyauto/flx/", "")

        for gap in sorted(file_gaps, key=lambda x: x["line"]):
            {
                "class": "🏗️",
                "function": "⚙️",
                "method": "🔧",
                "async_function": "⚡",
                "async_method": "⚡",
            }.get(gap["type"], "❓")

            f" (in {gap['parent_class']})" if gap["parent_class"] else ""

    # Summary by type
    gap_types = {}
    for gap in gaps:
        gap_type = gap["type"]
        gap_types[gap_type] = gap_types.get(gap_type, 0) + 1

    for gap_type, count in sorted(gap_types.items(), key=lambda x: x[1], reverse=True):
        pass

    return gaps


if __name__ == "__main__":
    main()
