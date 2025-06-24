#!/usr/bin/env python3
"""Build inventory of all Flx classes and functions for mypy fixes."""

import ast
import json
from pathlib import Path
from typing import Any


class FlxInventoryBuilder(ast.NodeVisitor):
    """AST visitor to build inventory of Flx classes and functions."""

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        self.classes: dict[str, dict[str, Any]] = {}
        self.functions: dict[str, dict[str, Any]] = {}
        self.imports: list[dict[str, Any]] = []
        self.current_class: str | None = None

    def visit_class_def(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        old_class = self.current_class
        self.current_class = node.name

        # Get base classes
        bases: list = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(
                    f"{base.value.id}.{base.attr}"
                    if isinstance(base.value, ast.Name)
                    else base.attr
                )

        # Get required init args
        init_args: list = []
        init_method = None
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                init_method = item
                break

        if init_method:
            for arg in init_method.args.args[1:]:  # Skip self
                init_args.append(
                    {
                        "name": arg.arg,
                        "has_default": False,
                        "annotation": ast.unparse(arg.annotation)
                        if arg.annotation
                        else None,
                    }
                )

            # Check defaults
            defaults_start = len(init_method.args.args) - len(init_method.args.defaults)
            for i, default in enumerate(init_method.args.defaults):
                arg_idx = defaults_start + i - 1  # -1 for self
                if arg_idx >= 0 and arg_idx < len(init_args):
                    init_args[arg_idx]["has_default"] = True
                    init_args[arg_idx]["default"] = ast.unparse(default)

        self.classes[node.name] = {
            "file": self.filepath,
            "line": node.lineno,
            "bases": bases,
            "init_args": init_args,
            "decorators": [ast.unparse(d) for d in node.decorator_list],
            "is_flx_prefixed": node.name.startswith("Flx"),
            "methods": [],
        }

        # Visit methods
        self.generic_visit(node)
        self.current_class = old_class

    def visit_function_def(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        func_info = {
            "name": node.name,
            "file": self.filepath,
            "line": node.lineno,
            "is_flx_prefixed": node.name.startswith("flx_"),
            "decorators": [ast.unparse(d) for d in node.decorator_list],
            "args": [],
        }

        # Get arguments
        for arg in node.args.args:
            if arg.arg not in {"self", "cls"}:
                func_info["args"].append(
                    {
                        "name": arg.arg,
                        "annotation": ast.unparse(arg.annotation)
                        if arg.annotation
                        else None,
                    }
                )

        if self.current_class:
            # It's a method
            self.classes[self.current_class]["methods"].append(func_info)
            # It's a module-level function
            self.functions[node.name] = func_info

        self.generic_visit(node)

    def visit_import(self, node: ast.Import) -> None:
        """Visit import statements."""
        for alias in node.names:
            self.imports.append(
                {
                    "module": alias.name,
                    "name": alias.asname or alias.name,
                    "line": node.lineno,
                }
            )
        self.generic_visit(node)

    def visit_import_from(self, node: ast.ImportFrom) -> None:
        """Visit from...import statements."""
        module = node.module or ""
        for alias in node.names:
            self.imports.append(
                {
                    "module": module,
                    "name": alias.name,
                    "asname": alias.asname,
                    "line": node.lineno,
                }
            )
        self.generic_visit(node)


def build_inventory(src_dir: Path) -> dict[str, Any]:
    """Build complete inventory of Flx codebase."""
    inventory = {
        "classes": {},
        "functions": {},
        "imports_by_file": {},
        "class_name_mapping": {},  # Maps non-Flx names to Flx names
        "function_name_mapping": {},  # Maps non-flx names to flx names
        "missing_flx_prefixes": {
            "classes": [],
            "functions": [],
        },
    }

    # Process all Python files
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            content = py_file.read_text()
            tree = ast.parse(content)

            visitor = FlxInventoryBuilder(str(py_file.relative_to(src_dir.parent)))
            visitor.visit(tree)

            # Merge results
            inventory["classes"].update(visitor.classes)
            inventory["functions"].update(visitor.functions)
            inventory["imports_by_file"][str(py_file)] = visitor.imports

        except Exception as e:
            print(f"Error processing {py_file}: {e}")

    # Build mappings and find missing prefixes
    for class_name, class_info in inventory["classes"].items():
        if class_name.startswith("Flx"):
            # Map non-Flx version to Flx version
            non_flx_name = class_name[3:]  # Remove Flx prefix
            inventory["class_name_mapping"][non_flx_name] = class_name
            # Check if Flx version exists
            flx_name = f"Flx{class_name}"
            if flx_name in inventory["classes"]:
                inventory["class_name_mapping"][class_name] = flx_name
                inventory["missing_flx_prefixes"]["classes"].append(
                    {
                        "name": class_name,
                        "file": class_info["file"],
                        "line": class_info["line"],
                    }
                )

    for func_name, func_info in inventory["functions"].items():
        if func_name.startswith("flx_"):
            # Map non-flx version to flx version
            non_flx_name = func_name[4:]  # Remove flx_ prefix
            inventory["function_name_mapping"][non_flx_name] = func_name
            # Check if flx version exists
            flx_name = f"flx_{func_name}"
            if flx_name in inventory["functions"]:
                inventory["function_name_mapping"][func_name] = flx_name
                inventory["missing_flx_prefixes"]["functions"].append(
                    {
                        "name": func_name,
                        "file": func_info["file"],
                        "line": func_info["line"],
                    }
                )

    # Analyze method prefixes
    for class_name, class_info in inventory["classes"].items():
        if class_name.startswith("Flx"):
            for method in class_info["methods"]:
                if not method["name"].startswith("_") and not method["name"].startswith(
                    "flx_"
                ):
                    if method["name"] not in {
                        "__init__",
                        "__str__",
                        "__repr__",
                        "__eq__",
                        "__hash__",
                    }:
                        inventory["missing_flx_prefixes"]["functions"].append(
                            {
                                "name": f"{class_name}.{method['name']}",
                                "file": method["file"],
                                "line": method["line"],
                                "is_method": True,
                                "class": class_name,
                            }
                        )

    return inventory


def analyze_mypy_errors(inventory: dict[str, Any], mypy_output: str) -> dict[str, Any]:
    """Analyze mypy errors against inventory."""
    analysis = {
        "attr_defined_fixes": [],
        "name_defined_fixes": [],
        "call_arg_fixes": [],
        "import_fixes": [],
    }

    lines = mypy_output.strip().split("\n")
    for line in lines:
        if "[attr-defined]" in line and "maybe" in line:
            # Extract suggestion
            parts = line.split('maybe "')
            if len(parts) > 1:
                suggestion = parts[1].split('"')[0]
                analysis["attr_defined_fixes"].append(
                    {
                        "line": line,
                        "suggestion": suggestion,
                    }
                )

        elif "[name-defined]" in line:
            # Extract undefined name
            if '"' in line:
                parts = line.split('"')
                if len(parts) >= 2:
                    undefined_name = parts[1]
                    # Check if we have a mapping
                    if undefined_name in inventory["class_name_mapping"]:
                        analysis["name_defined_fixes"].append(
                            {
                                "line": line,
                                "undefined": undefined_name,
                                "fix": inventory["class_name_mapping"][undefined_name],
                            }
                        )

    return analysis


def main() -> None:
    """Main function."""
    src_dir = Path("/home/marlonsc/pyauto/flx/src")

    print("Building FLX inventory...")
    inventory = build_inventory(src_dir)

    # Save inventory
    output_file = Path("/home/marlonsc/pyauto/flx_inventory.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, default=str)

    print(f"\nInventory saved to: {output_file}")
    print("\nSummary:")
    print(f"- Total classes: {len(inventory['classes'])}")
    print(
        f"- Flx-prefixed classes: {sum(1 for c in inventory['classes'].values() if c['is_flx_prefixed'])}"
    )
    print(f"- Total functions: {len(inventory['functions'])}")
    print(
        f"- flx-prefixed functions: {sum(1 for f in inventory['functions'].values() if f['is_flx_prefixed'])}"
    )
    print(f"- Class name mappings: {len(inventory['class_name_mapping'])}")
    print(f"- Function name mappings: {len(inventory['function_name_mapping'])}")
    print("\nMissing prefixes:")
    print(
        f"- Classes without Flx prefix: {len(inventory['missing_flx_prefixes']['classes'])}"
    )
    print(
        f"- Functions/methods without flx_ prefix: {len(inventory['missing_flx_prefixes']['functions'])}"
    )

    # Show some examples
    if inventory["class_name_mapping"]:
        print("\nExample class mappings:")
        for old, new in list(inventory["class_name_mapping"].items())[:5]:
            print(f"  {old} -> {new}")

    if inventory["function_name_mapping"]:
        print("\nExample function mappings:")
        for old, new in list(inventory["function_name_mapping"].items())[:5]:
            print(f"  {old} -> {new}")


if __name__ == "__main__":
    main()
