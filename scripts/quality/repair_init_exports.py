#!/usr/bin/env python3
"""Repair __all__ exports in all target files."""

from __future__ import annotations

import ast
import re
from collections.abc import Iterable
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]

TARGET_GLOBS = [
    "**/src/*/__init__.py",
]

# Names that are safe to export even if dunder
ALWAYS_INCLUDE = {"__version__", "__version_info__"}

# Names that we should never export
NEVER_EXPORT = {
    # common stdlib modules accidentally imported
    "os",
    "sys",
    "warnings",
    "typing",
    "types",
    "importlib",
    "contextlib",
    # local helpers with underscores will be filtered separately
}

ASSIGN_NAME_RE = re.compile(r"^\w+$")


def iter_target_files() -> Iterable[Path]:
    """Iterate over all target files."""
    for pattern in TARGET_GLOBS:
        for path in WORKSPACE.glob(pattern):
            # skip virtualenvs or build dirs just in case
            parts = {p.lower() for p in path.parts}
            if any(
                x in parts
                for x in (
                    ".venv",
                    "venv",
                    "site-packages",
                    "build",
                    "dist",
                    "node_modules",
                )
            ):
                continue
            yield path


def parse_public_exports(py_path: Path) -> list[str]:
    """Parse the public exports from a Python file."""
    src = py_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []

    existing_all: list[str] = []
    # collect existing __all__ entries to preserve order
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    try:
                        value = ast.literal_eval(node.value)
                    except Exception:
                        value = None
                    if isinstance(value, (list, tuple)):
                        existing_all = [str(x) for x in value]
                    break

    names: list[str] = []

    def add(name: str) -> None:
        """Add a name to the list of public exports."""
        if not name:
            return
        if name.startswith("_") and name not in ALWAYS_INCLUDE:
            return
        if name in NEVER_EXPORT:
            return
        if name not in names:
            names.append(name)

    # Add imported names (from ... import ...)
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            # Skip star imports
            for alias in node.names:
                if alias.name == "*":
                    continue
                add(alias.asname or alias.name)

    # Add defined functions/classes and simple assigns
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets: list[ast.expr] = []
            if isinstance(node, ast.Assign):
                targets = [t for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node.target, ast.Name):
                targets = [node.target]
            for t in targets:
                if not isinstance(t, ast.Name):
                    continue
                name = t.id
                # Ignore the __all__ variable itself
                if name == "__all__":
                    continue
                if name in ALWAYS_INCLUDE:
                    add(name)
                    continue
                # Only add simple constants/aliases that look like public API
                if name and not name.startswith("_"):
                    add(name)

    # Merge with existing __all__ (preserve its order first)
    ordered: list[str] = []
    seen: set[str] = set()
    for n in existing_all:
        if n not in seen:
            ordered.append(n)
            seen.add(n)
    for n in names:
        if n not in seen:
            ordered.append(n)
            seen.add(n)

    # Ensure deterministic order without destroying intent: keep existing order, then sort new ones appended
    # Above already preserves sequence; to add minimal stability, return as-is
    return ordered


def replace_or_append_all(py_path: Path, exports: list[str]) -> bool:
    """Replace the __all__ definition, or append if not present.

    Returns True if file content changed.
    """
    src = py_path.read_text(encoding="utf-8")

    # Build pretty-printed __all__ block
    # Wrap lines to a reasonable length
    lines: list[str] = []
    current: list[str] = []
    max_len = 100

    def flush_current() -> None:
        """Flush the current list of exports."""
        if current:
            lines.append(", ".join(current))
            current.clear()

    for name in exports:
        item = f'"{name}"'
        # decide if adding will exceed limit
        tentative = ", ".join([*current, item]) if current else item
        if len(tentative) > max_len:
            flush_current()
            current.append(item)
        else:
            current.append(item)
    flush_current()

    pretty = "__all__: list[str] = [\n    " + ",\n    ".join(lines) + ",\n]"

    pattern = re.compile(r"^__all__\s*[:=].*", re.DOTALL | re.MULTILINE)

    # Try to find existing __all__ assignment region more robustly by AST spans
    replaced = False
    try:
        tree = ast.parse(src)
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        # Replace exact node text range if possible
                        # Fallback to regex replace
                        replaced = True
                        break
            elif (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "__all__"
            ):
                replaced = True
                break
    except SyntaxError:
        pass

    new_src: str
    if replaced:
        # Replace the first occurrence using a simple strategy: find the __all__ line and replace until matching closing bracket
        # Find start index
        start_idx = src.find("__all__")
        if start_idx != -1:
            # Find the opening bracket after start
            open_idx = src.find("[", start_idx)
            if open_idx != -1:
                # Find matching closing bracket by counting brackets
                depth = 0
                end_idx = open_idx
                while end_idx < len(src):
                    ch = src[end_idx]
                    if ch == "[":
                        depth += 1
                    elif ch == "]":
                        depth -= 1
                        if depth == 0:
                            end_idx += 1  # include closing bracket
                            break
                    end_idx += 1
                if end_idx > open_idx:
                    new_src = src[:start_idx] + pretty + src[end_idx:]
                else:
                    # Failed bracket scan, fallback to regex
                    new_src = pattern.sub(pretty, src, count=1)
            else:
                new_src = pattern.sub(pretty, src, count=1)
        else:
            new_src = pattern.sub(pretty, src, count=1)
    else:
        # Append at end with two newlines
        new_src = src.rstrip() + "\n\n" + pretty + "\n"

    if new_src != src:
        py_path.write_text(new_src, encoding="utf-8")
        return True
    return False


def main() -> None:
    """Main function to repair __all__ exports in all target files."""
    changed_files: list[Path] = []
    for path in iter_target_files():
        exports = parse_public_exports(path)
        if not exports:
            continue
        if replace_or_append_all(path, exports):
            changed_files.append(path)
    if changed_files:
        for p in changed_files:
            p.relative_to(WORKSPACE)


if __name__ == "__main__":
    main()
