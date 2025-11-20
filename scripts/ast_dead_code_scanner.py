#!/usr/bin/env python3
"""AST-based Dead Code Scanner for FLEXT Projects.

Scans Python files to identify:
- Functions defined but never called
- Classes defined but never instantiated
- Methods defined but never invoked
- Unused imports
- Unused constants

Usage:
    python ast_dead_code_scanner.py [--projects PROJECT1 PROJECT2 ...]
    python ast_dead_code_scanner.py --all
    python ast_dead_code_scanner.py --output report.json
"""

from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Symbol:
    """Represents a code symbol (function, class, method, constant)."""

    name: str
    kind: str  # function, class, method, constant, import
    file: Path
    line: int
    parent: str | None = None  # For methods: parent class name
    usages: list[tuple[Path, int]] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        """Get fully qualified name."""
        if self.parent:
            return f"{self.parent}.{self.name}"
        return self.name


class DeadCodeScanner:
    """Scans Python codebase for dead code using AST analysis."""

    def __init__(self, base_path: Path) -> None:
        """Initialize scanner with base path."""
        self.base_path = base_path
        self.symbols: dict[str, Symbol] = {}
        self.usages: dict[str, list[tuple[Path, int]]] = defaultdict(list)
        self.imports: dict[str, list[tuple[Path, int]]] = defaultdict(list)
        self.errors: list[str] = []

    def scan_directory(self, directory: Path) -> None:
        """Scan all Python files in a directory."""
        if not directory.exists():
            self.errors.append(f"Directory not found: {directory}")
            return

        for py_file in directory.rglob("*.py"):
            # Skip test files and __pycache__
            if "__pycache__" in str(py_file) or "/.venv/" in str(py_file):
                continue
            self._scan_file(py_file)

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single Python file."""
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source, filename=str(file_path))

            # Phase 1: Collect definitions
            self._collect_definitions(tree, file_path)

            # Phase 2: Collect usages
            self._collect_usages(tree, file_path)

        except SyntaxError as e:
            self.errors.append(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            self.errors.append(f"Error scanning {file_path}: {e}")

    def _collect_definitions(self, tree: ast.AST, file_path: Path) -> None:
        """Collect all symbol definitions from AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                # Check if it's a method (inside a class)
                parent = self._get_parent_class(tree, node)
                kind = "method" if parent else "function"

                # Skip private methods starting with _ (except __init__)
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue

                symbol = Symbol(
                    name=node.name,
                    kind=kind,
                    file=file_path,
                    line=node.lineno,
                    parent=parent,
                )
                key = f"{file_path}:{symbol.full_name}"
                self.symbols[key] = symbol

            elif isinstance(node, ast.ClassDef):
                # Skip private classes
                if node.name.startswith("_"):
                    continue

                symbol = Symbol(
                    name=node.name,
                    kind="class",
                    file=file_path,
                    line=node.lineno,
                )
                key = f"{file_path}:{node.name}"
                self.symbols[key] = symbol

            elif isinstance(node, ast.Assign):
                # Check for constants (UPPER_CASE at module level)
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id.isupper() and "_" in target.id:
                            symbol = Symbol(
                                name=target.id,
                                kind="constant",
                                file=file_path,
                                line=node.lineno,
                            )
                            key = f"{file_path}:{target.id}"
                            self.symbols[key] = symbol

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    name = alias.asname or alias.name
                    self.imports[name].append((file_path, node.lineno))

    def _get_parent_class(
        self, tree: ast.AST, func_node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> str | None:
        """Get parent class name for a function node if it's a method."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for child in ast.walk(node):
                    if child is func_node:
                        return node.name
        return None

    def _collect_usages(self, tree: ast.AST, file_path: Path) -> None:
        """Collect all symbol usages from AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                # Variable/function name usage
                self.usages[node.id].append((file_path, node.lineno))

            elif isinstance(node, ast.Attribute):
                # Attribute access (e.g., obj.method)
                if isinstance(node.value, ast.Name):
                    full_name = f"{node.value.id}.{node.attr}"
                    self.usages[node.attr].append((file_path, node.lineno))
                    self.usages[full_name].append((file_path, node.lineno))
                else:
                    self.usages[node.attr].append((file_path, node.lineno))

            elif isinstance(node, ast.Call):
                # Function/method call
                if isinstance(node.func, ast.Name):
                    self.usages[node.func.id].append((file_path, node.lineno))
                elif isinstance(node.func, ast.Attribute):
                    self.usages[node.func.attr].append((file_path, node.lineno))

    def find_dead_code(self) -> dict[str, list[dict[str, Any]]]:
        """Find unused symbols."""
        dead_code: dict[str, list[dict[str, Any]]] = {
            "functions": [],
            "classes": [],
            "methods": [],
            "constants": [],
        }

        for symbol in self.symbols.values():
            # Get usage count
            usage_count = len(self.usages.get(symbol.name, []))

            # For methods, also check full_name usage
            if symbol.parent:
                usage_count += len(self.usages.get(symbol.full_name, []))

            # Consider a symbol unused if it has 0 or 1 usage (self-definition)
            if usage_count <= 1:
                # Calculate confidence
                confidence = self._calculate_confidence(symbol, usage_count)

                if confidence >= 0.5:  # Only report if confidence >= 50%
                    entry = {
                        "name": symbol.full_name,
                        "file": str(symbol.file.relative_to(self.base_path)),
                        "line": symbol.line,
                        "confidence": confidence,
                        "usages": usage_count,
                    }

                    if symbol.kind == "function":
                        dead_code["functions"].append(entry)
                    elif symbol.kind == "class":
                        dead_code["classes"].append(entry)
                    elif symbol.kind == "method":
                        dead_code["methods"].append(entry)
                    elif symbol.kind == "constant":
                        dead_code["constants"].append(entry)

        # Sort by confidence (highest first)
        for category in dead_code:
            dead_code[category].sort(key=lambda x: -x["confidence"])

        return dead_code

    def _calculate_confidence(self, symbol: Symbol, usage_count: int) -> float:
        """Calculate confidence score for dead code detection."""
        confidence = 0.0

        # Base confidence based on usage
        if usage_count == 0:
            confidence = 0.9
        elif usage_count == 1:
            confidence = 0.6

        # Lower confidence for special names
        if symbol.name.startswith("__") and symbol.name.endswith("__"):
            confidence *= 0.3  # Magic methods are often called implicitly
        elif symbol.name in {"main", "setup", "teardown", "run"}:
            confidence *= 0.5  # Common entry points
        elif symbol.kind == "method" and symbol.name in {
            "__init__",
            "__str__",
            "__repr__",
        }:
            confidence *= 0.3  # Often called implicitly

        # Lower confidence for test-related names
        if "test" in str(symbol.file).lower():
            confidence *= 0.7

        return min(confidence, 1.0)

    def generate_report(self) -> dict[str, Any]:
        """Generate full report."""
        dead_code = self.find_dead_code()

        total_dead = sum(len(items) for items in dead_code.values())
        total_symbols = len(self.symbols)

        return {
            "summary": {
                "total_symbols": total_symbols,
                "total_dead_code": total_dead,
                "dead_percentage": round(total_dead / max(total_symbols, 1) * 100, 2),
                "errors": len(self.errors),
            },
            "dead_code": dead_code,
            "errors": self.errors[:20],  # Limit errors
        }


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="AST Dead Code Scanner for FLEXT")
    parser.add_argument(
        "--projects",
        nargs="+",
        default=["flext-ldif"],
        help="Projects to scan (default: flext-ldif)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan all FLEXT projects",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="",
        help="Output file (JSON format)",
    )
    parser.add_argument(
        "--src-only",
        action="store_true",
        default=True,
        help="Only scan src directories",
    )

    args = parser.parse_args()

    base_path = Path("/home/marlonsc/flext")

    if args.all:
        projects = [
            "flext-ldif",
            "flext-core",
            "flext-cli",
            "flext-ldap",
            "client-a-oud-mig",
        ]
    else:
        projects = args.projects

    scanner = DeadCodeScanner(base_path)

    print(f"Scanning {len(projects)} projects...")

    for project in projects:
        project_path = base_path / project
        scan_path = project_path / "src" if args.src_only else project_path

        if scan_path.exists():
            print(f"  Scanning {project}/src...")
            scanner.scan_directory(scan_path)
        else:
            print(f"  Skipping {project} (not found)")

    report = scanner.generate_report()

    # Print summary
    summary = report["summary"]
    print("\n" + "=" * 60)
    print("DEAD CODE ANALYSIS REPORT")
    print("=" * 60)
    print(f"Total symbols analyzed: {summary['total_symbols']}")
    print(f"Potentially dead code:  {summary['total_dead_code']}")
    print(f"Dead code percentage:   {summary['dead_percentage']}%")
    print(f"Parse errors:           {summary['errors']}")
    print("=" * 60)

    # Print dead code by category
    dead_code = report["dead_code"]

    for category, items in dead_code.items():
        if items:
            print(f"\n{category.upper()} ({len(items)} items):")
            for item in items[:10]:  # Show top 10
                print(f"  - {item['name']}")
                print(f"    File: {item['file']}:{item['line']}")
                print(f"    Confidence: {item['confidence']:.0%}")

    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        with Path(output_path).open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nFull report saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
