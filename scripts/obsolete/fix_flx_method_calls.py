#!/usr/bin/env python3
"""Fix method calls missing flx_ prefix in FLX codebase."""

import ast
import json
from pathlib import Path
from typing import Any


class MethodCallFixer(ast.NodeTransformer):
    """AST transformer to fix method calls missing flx_ prefix."""

    def __init__(self, inventory: dict[str, Any]) -> None:
        self.inventory = inventory
        self.changes_made: list[dict[str, Any]] = []
        self.current_class: str | None = None
        self.imported_names: set[str] = set()

    def visit_class_def(self, node: ast.ClassDef) -> Any:
        """Track current class context."""
        old_class = self.current_class
        self.current_class = node.name
        result = self.generic_visit(node)
        self.current_class = old_class
        return result

    def visit_import(self, node: ast.Import) -> Any:
        """Track imported names."""
        for alias in node.names:
            self.imported_names.add(alias.asname or alias.name)
        return node

    def visit_import_from(self, node: ast.ImportFrom) -> Any:
        """Track imported names."""
        for alias in node.names:
            self.imported_names.add(alias.asname or alias.name)
        return node

    def visit_Call(self, node: ast.Call) -> Any:
        """Fix method calls to use flx_ prefix."""
        node = self.generic_visit(node)

        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr

            # Skip if already has flx_ prefix or is a dunder method
            if method_name.startswith(("flx_", "_")):
                return node

            # Check if this method should have flx_ prefix
            should_fix = False
            context_info = ""

            # Check if calling on self or instance of Flx class
            if isinstance(node.func.value, ast.Name):
                var_name = node.func.value.id
                if (
                    var_name == "self"
                    and self.current_class
                    and self.current_class.startswith("Flx")
                ):
                    should_fix = True
                    context_info = f"self in {self.current_class}"
                elif var_name in self.imported_names:
                    # Check if it's an Flx class instance
                    should_fix = self._is_flx_instance_var(var_name)
                    context_info = f"variable {var_name}"

            # Check if the flx_ version exists in inventory
            flx_method_name = f"flx_{method_name}"
            if should_fix and self._method_exists_in_inventory(flx_method_name):
                # Apply fix
                old_name = node.func.attr
                node.func.attr = flx_method_name

                self.changes_made.append(
                    {
                        "type": "method_call",
                        "old": old_name,
                        "new": flx_method_name,
                        "line": node.lineno if hasattr(node, "lineno") else 0,
                        "context": context_info,
                    },
                )

        return node

    def _is_flx_instance_var(self, var_name: str) -> bool:
        """Check if variable is likely an instance of Flx class."""
        # Simple heuristic - can be improved with type inference
        flx_indicators = [
            "client",
            "service",
            "manager",
            "handler",
            "builder",
            "formatter",
            "adapter",
            "factory",
            "registry",
            "publisher",
        ]
        return any(ind in var_name.lower() for ind in flx_indicators)

    def _method_exists_in_inventory(self, method_name: str) -> bool:
        """Check if method exists in any Flx class."""
        for class_info in self.inventory["classes"].values():
            if class_info["is_flx_prefixed"]:
                for method in class_info["methods"]:
                    if method["name"] == method_name:
                        return True
        return False


def fix_file(
    filepath: Path, inventory: dict[str, Any], dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Fix method calls in a single file."""
    try:
        content = filepath.read_text()
        tree = ast.parse(content)

        fixer = MethodCallFixer(inventory)
        new_tree = fixer.visit(tree)

        if fixer.changes_made and not dry_run:
            # Generate new code
            new_content = ast.unparse(new_tree)
            filepath.write_text(new_content)

        return fixer.changes_made

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []


def main() -> None:
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix method calls missing flx_ prefix")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    parser.add_argument("--file", help="Fix specific file only")
    args = parser.parse_args()

    # Load inventory
    inventory_file = Path("/home/marlonsc/pyauto/flx_inventory.json")
    with open(inventory_file, encoding="utf-8") as f:
        inventory = json.load(f)

    src_dir = Path("/home/marlonsc/pyauto/flx/src")

    files = [Path(args.file)] if args.file else list(src_dir.rglob("*.py"))

    total_changes = 0
    files_changed = 0

    print(f"Processing {len(files)} files...")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLYING FIXES'}")
    print()

    for filepath in files:
        if "__pycache__" in str(filepath):
            continue

        changes = fix_file(filepath, inventory, args.dry_run)

        if changes:
            files_changed += 1
            total_changes += len(changes)

            print(f"\n{filepath.relative_to(src_dir.parent)}:")
            for change in changes:
                print(
                    f"  Line {change['line']}: {change['old']} -> {change['new']} ({
                        change['context']
                    })",
                )

    print("\nSummary:")
    print(f"- Files processed: {len(files)}")
    print(f"- Files with changes: {files_changed}")
    print(f"- Total changes: {total_changes}")

    if args.dry_run:
        print("\nThis was a dry run. Use without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
