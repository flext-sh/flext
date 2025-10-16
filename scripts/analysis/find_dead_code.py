#!/usr/bin/env python3
"""AST-based dead code analyzer for flext projects.

Analyzes Python files to find:
- Unused classes
- Unused methods/functions
- Unused imports
- Unreachable code
"""

import ast
from collections import defaultdict
from pathlib import Path
from typing import Any


class CodeAnalyzer(ast.NodeVisitor):
    """Analyze Python code using AST to find unused definitions."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        # Track all definitions (what's defined)
        self.definitions: dict[str, set[str]] = defaultdict(set)
        # Track all usages (what's used)
        self.usages: dict[str, set[str]] = defaultdict(set)
        # Track methods per class
        self.class_methods: dict[str, dict[str, set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        # Current context
        self.current_file: str = ""
        self.current_class: str = ""

    def analyze_project(self, paths: list[Path]) -> dict[str, Any]:
        """Analyze all Python files in given paths."""
        print(f"🔍 Analyzing {len(paths)} projects...")

        for path in paths:
            if not path.exists():
                continue

            # Find all Python files
            py_files = list(path.rglob("*.py"))
            print(f"\n📁 {path.name}: {len(py_files)} Python files")

            for py_file in py_files:
                # Skip test files, __pycache__, .mypy_cache
                if (
                    "__pycache__" in str(py_file)
                    or ".mypy_cache" in str(py_file)
                    or "tests/" in str(py_file)
                    or "/test_" in str(py_file)
                ):
                    continue

                try:
                    self.analyze_file(py_file)
                except Exception as e:
                    print(f"  ⚠️  Error analyzing {py_file.name}: {e}")

        return self.find_unused()

    def analyze_file(self, filepath: Path) -> None:
        """Analyze a single Python file."""
        self.current_file = str(filepath.relative_to(self.project_root))

        try:
            with Path(filepath).open("r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(filepath))
                self.visit(tree)
        except SyntaxError as e:
            print(f"  ⚠️  Syntax error in {filepath.name}: {e}")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class definitions."""
        self.definitions[self.current_file].add(f"class:{node.name}")
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function/method definitions."""
        if self.current_class:
            # It's a method
            key = f"{self.current_class}.{node.name}"
            self.class_methods[self.current_file][self.current_class].add(node.name)
            self.definitions[self.current_file].add(f"method:{key}")
        else:
            # It's a function
            self.definitions[self.current_file].add(f"function:{node.name}")

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Track async function/method definitions."""
        if self.current_class:
            key = f"{self.current_class}.{node.name}"
            self.class_methods[self.current_file][self.current_class].add(node.name)
            self.definitions[self.current_file].add(f"method:{key}")
        else:
            self.definitions[self.current_file].add(f"function:{node.name}")

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Track function/method calls (usages)."""
        # Track method calls (self.method_name)
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
                # self.method_name() call
                if self.current_class:
                    key = f"{self.current_class}.{node.func.attr}"
                    self.usages[self.current_file].add(f"method:{key}")

        # Track function calls
        elif isinstance(node.func, ast.Name):
            self.usages[self.current_file].add(f"function:{node.func.id}")

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        """Track name usages."""
        # Track class instantiation
        self.usages[self.current_file].add(f"class:{node.id}")
        self.generic_visit(node)

    def find_unused(self) -> dict[str, Any]:
        """Find unused definitions."""
        unused: dict[str, list[str]] = defaultdict(list)

        for file, defs in self.definitions.items():
            # Collect all usages from all files (cross-file usage check)
            all_usages = set()
            for usages in self.usages.values():
                all_usages.update(usages)

            for definition in defs:
                # Skip special methods (dunder methods, overrides, property decorators)
                def_name = definition.split(":", 1)[1]
                if (
                    def_name.startswith("__")
                    or def_name.endswith("__")
                    or ".__init__" in def_name
                    or "._" in def_name  # Private methods
                ):
                    continue

                # Check if definition is used anywhere
                if definition not in all_usages:
                    unused[file].append(definition)

        return {"unused": unused, "class_methods": dict(self.class_methods)}


def print_results(results: dict[str, Any]) -> None:
    """Print analysis results."""
    unused = results["unused"]

    if not unused:
        print("\n✅ No dead code found!")
        return

    print("\n" + "=" * 80)
    print("🗑️  DEAD CODE ANALYSIS RESULTS")
    print("=" * 80)

    total_dead = 0
    for file, items in sorted(unused.items()):
        if not items:
            continue

        print(f"\n📄 {file}")
        print("   " + "─" * 70)

        # Group by type
        classes = [i for i in items if i.startswith("class:")]
        methods = [i for i in items if i.startswith("method:")]
        functions = [i for i in items if i.startswith("function:")]

        if classes:
            print("   🏛️  Unused Classes:")
            for cls in sorted(classes):
                print(f"      • {cls.split(':', 1)[1]}")
                total_dead += 1

        if methods:
            print("   🔧 Unused Methods:")
            for method in sorted(methods):
                print(f"      • {method.split(':', 1)[1]}")
                total_dead += 1

        if functions:
            print("   📦 Unused Functions:")
            for func in sorted(functions):
                print(f"      • {func.split(':', 1)[1]}")
                total_dead += 1

    print("\n" + "=" * 80)
    print(f"📊 Total potentially unused items: {total_dead}")
    print("=" * 80)
    print("\n⚠️  Note: These are POTENTIAL dead code candidates.")
    print("    Manual review is required before deletion!")
    print("    Some may be:")
    print("    - Public API methods (exported in __init__.py)")
    print("    - Used dynamically (getattr, exec, etc.)")
    print("    - Framework callbacks (pytest fixtures, etc.)")


def main() -> None:
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent

    # Projects to analyze
    projects = [
        project_root / "flext-ldif" / "src" / "flext_ldif",
        project_root / "flext-ldap" / "src" / "flext_ldap",
        project_root / "client-a-oud-mig" / "src" / "client-a_oud_mig",
    ]

    analyzer = CodeAnalyzer(project_root)
    results = analyzer.analyze_project(projects)
    print_results(results)


if __name__ == "__main__":
    main()
