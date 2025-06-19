#!/usr/bin/env python3
"""Fix remaining FLX mypy issues including imports, exceptions, and method calls."""

import ast
import json
import re
from pathlib import Path


class FlxImportFixer(ast.NodeTransformer):
    """Fix import issues in FLX code."""

    def __init__(self) -> None:
        self.changes: list[dict[str, any]] = []
        self.imported_names: set[str] = set()

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Fix from...import statements."""
        # Fix hookspecs imports
        if node.module and "hookspecs" in node.module:
            new_names = []
            changed = False

            for alias in node.names:
                name = alias.name
                # Add flx_ prefix to hook functions
                if name.startswith("register_") and not name.startswith("flx_"):
                    new_name = f"flx_{name}"
                    new_alias = ast.alias(name=new_name, asname=alias.asname or name)
                    new_names.append(new_alias)
                    changed = True
                    self.changes.append(
                        {
                            "type": "import_function",
                            "old": name,
                            "new": new_name,
                            "line": node.lineno,
                        }
                    )
                else:
                    new_names.append(alias)

            if changed:
                node.names = new_names

        return node


class FlxExceptionFixer(ast.NodeTransformer):
    """Fix exception attribute access patterns."""

    def __init__(self) -> None:
        self.changes: list[dict[str, any]] = []

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        """Fix private attribute access on exceptions."""
        node = self.generic_visit(node)

        # Check if accessing private attributes on exception objects
        if isinstance(node.value, ast.Name) and "exception" in node.value.id.lower():
            if node.attr in {"_context", "_details", "_error_chain"}:
                # Replace with getattr call
                new_node = ast.Call(
                    func=ast.Name(id="getattr", ctx=ast.Load()),
                    args=[
                        node.value,
                        ast.Constant(value=node.attr),
                        ast.Constant(value=None),
                    ],
                    keywords=[],
                )
                self.changes.append(
                    {
                        "type": "exception_attr",
                        "old": f"{node.value.id}.{node.attr}",
                        "new": f"getattr({node.value.id}, '{node.attr}', None)",
                        "line": node.lineno if hasattr(node, "lineno") else 0,
                    }
                )
                return new_node

        return node


def fix_missing_imports(filepath: Path) -> list[dict[str, any]]:
    """Fix missing imports based on undefined names."""
    changes = []

    # Common missing imports map
    import_map = {
        "scan_object": "from flx.infra.async.pluggable_publisher import flx_scan_object",
        "FlxError": "from flx.core.exceptions import FlxError",
        "CorrelationId": "from flx.infra.logging.domain import FlxCorrelationId as CorrelationId",
        "ComponentPath": "from flx.infra.logging.domain import FlxComponentPath as ComponentPath",
        "LogSession": "from flx.infra.logging.domain import FlxLogSession as LogSession",
        "LogStream": "from flx.infra.logging.domain import FlxLogStream as LogStream",
        "LogEntryCreated": "from flx.infra.logging.domain import FlxLogEntryCreated as LogEntryCreated",
        "HighErrorRateDetected": "from flx.infra.logging.domain import FlxHighErrorRateDetected as HighErrorRateDetected",
        "LogSessionCompleted": "from flx.infra.logging.domain import FlxLogSessionCompleted as LogSessionCompleted",
    }

    try:
        content = filepath.read_text()
        lines = content.splitlines()

        # Find import section (before first class/function)
        import_end_line = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith(("import ", "from ", "#", '"""')):
                if not line.strip().startswith("__"):
                    import_end_line = i
                    break

        # Check for undefined names and add imports
        added_imports = set()
        for name, import_stmt in import_map.items():
            if re.search(rf"\b{name}\b", content) and import_stmt not in content:
                if import_stmt not in added_imports:
                    lines.insert(import_end_line, import_stmt)
                    added_imports.add(import_stmt)
                    import_end_line += 1
                    changes.append(
                        {
                            "type": "add_import",
                            "import": import_stmt,
                            "for": name,
                        }
                    )

        if changes:
            filepath.write_text("\n".join(lines) + "\n")

    except Exception as e:
        print(f"Error fixing imports in {filepath}: {e}")

    return changes


def fix_method_references(filepath: Path) -> list[dict[str, any]]:
    """Fix method references that are missing flx_ prefix."""
    changes = []

    # Map of methods that need flx_ prefix
    method_map = {
        ".validate_url(": ".flx_validate_url(",
        ".discover_api_structure(": ".flx_discover_api_structure(",
        ".publish_event(": ".flx_publish_event(",
        ".publish_events(": ".flx_publish_events(",
        ".format_and_display(": ".flx_format_and_display(",
        ".record_event(": ".flx_record_event(",
        ".get_metrics(": ".flx_get_metrics(",
        ".numeric_value": ".flx_numeric_value",
        ".full_path": ".flx_full_path",
        ".is_higher_than(": ".flx_is_higher_than(",
        ".create_child(": ".flx_create_child(",
        ".formatted_content": ".flx_formatted_content",
        ".is_empty(": ".flx_is_empty(",
        ".with_correlation(": ".flx_with_correlation(",
        ".with_trace(": ".flx_with_trace(",
        ".with_component(": ".flx_with_component(",
        ".add_tag(": ".flx_add_tag(",
        ".add_metadata(": ".flx_add_metadata(",
        ".is_error_level(": ".flx_is_error_level(",
        ".should_include_stack_trace(": ".flx_should_include_stack_trace(",
        ".finish(": ".flx_finish(",
        ".add_entry_stats(": ".flx_add_entry_stats(",
        ".error_rate": ".flx_error_rate",
        ".is_high_error_session": ".flx_is_high_error_session",
        ".start_session(": ".flx_start_session(",
        ".add_log_entry(": ".flx_add_log_entry(",
        ".finish_session(": ".flx_finish_session(",
        ".overall_error_rate": ".flx_overall_error_rate",
        ".is_healthy(": ".flx_is_healthy(",
        ".should_process(": ".flx_should_process(",
        ".transform(": ".flx_transform(",
        ".process(": ".flx_process(",
        ".handle_event(": ".flx_handle_event(",
        ".should_alert(": ".flx_should_alert(",
        ".send_alert(": ".flx_send_alert(",
        ".time_component(": ".flx_time_component(",
        ".generate_report(": ".flx_generate_report(",
    }

    try:
        content = filepath.read_text()
        original = content

        for old, new in method_map.items():
            if old in content:
                content = content.replace(old, new)
                changes.append(
                    {
                        "type": "method_reference",
                        "old": old,
                        "new": new,
                    }
                )

        if content != original:
            filepath.write_text(content)

    except Exception as e:
        print(f"Error fixing method references in {filepath}: {e}")

    return changes


def fix_constructor_calls(
    filepath: Path, inventory: dict[str, any]
) -> list[dict[str, any]]:
    """Fix constructor calls with missing arguments."""
    changes = []

    # Common constructor fixes
    constructor_defaults = {
        "FlxAdapterMeta": {
            "version": '"1.0.0"',
            "dependencies": "[]",
        },
        "FlxAdapterResult": {
            "message": '""',
            "error": "None",
            "metadata": "{}",
        },
        "FlxLogEntry": {
            "severity": "FlxLogSeverity.INFO",
        },
    }

    try:
        content = filepath.read_text()
        content.splitlines()

        for class_name, defaults in constructor_defaults.items():
            # Find constructor calls missing arguments
            pattern = rf"{class_name}\s*\([^)]*\)"
            matches = list(re.finditer(pattern, content))

            for match in reversed(matches):  # Process in reverse to maintain positions
                call_text = match.group()

                # Check if it's missing required args
                for arg_name, default_value in defaults.items():
                    if (
                        f"{arg_name}=" not in call_text
                        and f'"{arg_name}"' not in call_text
                    ):
                        # Add the missing argument
                        if ")" in call_text:
                            # Find the closing parenthesis
                            close_idx = call_text.rfind(")")
                            args_part = call_text[:close_idx]

                            # Add comma if there are existing args
                            if "(" in args_part and args_part.split("(")[1].strip():
                                new_call = f"{args_part}, {arg_name}={default_value})"
                            else:
                                new_call = (
                                    f"{args_part.rstrip()}{arg_name}={default_value})"
                                )

                            # Calculate line and position
                            start_pos = match.start()
                            line_num = content[:start_pos].count("\n")

                            # Replace in content
                            content = (
                                content[: match.start()]
                                + new_call
                                + content[match.end() :]
                            )

                            changes.append(
                                {
                                    "type": "constructor_arg",
                                    "class": class_name,
                                    "arg": arg_name,
                                    "value": default_value,
                                    "line": line_num + 1,
                                }
                            )

        if changes:
            filepath.write_text(content)

    except Exception as e:
        print(f"Error fixing constructor calls in {filepath}: {e}")

    return changes


def main() -> None:
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix remaining FLX issues")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed"
    )
    parser.add_argument(
        "--type",
        choices=["imports", "exceptions", "methods", "constructors", "all"],
        default="all",
        help="Type of fixes to apply",
    )
    args = parser.parse_args()

    # Load inventory
    inventory_file = Path("/home/marlonsc/pyauto/flx_inventory.json")
    with open(inventory_file, encoding="utf-8") as f:
        inventory = json.load(f)

    src_dir = Path("/home/marlonsc/pyauto/flx/src")

    # Files with known issues
    problem_files = [
        "flx/infra/exceptions/helpers.py",
        "flx/infra/async/pluggable_publisher.py",
        "flx/infra/logging/domain.py",
        "flx/infra/logging/shutdown_metrics.py",
        "flx/adapters/system.py",
        "flx/core/exceptions.py",
        "flx/infra/ldap/exceptions.py",
        "flx/infra/output.py",
        "flx/plugins/hookspecs/__init__.py",
    ]

    files = [src_dir / f for f in problem_files if (src_dir / f).exists()]

    print(f"Processing {len(files)} files...")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLYING FIXES'}")

    total_changes = 0

    for filepath in files:
        print(f"\n{filepath.relative_to(src_dir.parent)}:")
        file_changes = []

        if args.type in {"imports", "all"}:
            if not args.dry_run:
                import_changes = fix_missing_imports(filepath)
                file_changes.extend(import_changes)
            else:
                print("  Would fix missing imports")

        if args.type in {"exceptions", "all"}:
            try:
                content = filepath.read_text()
                tree = ast.parse(content)
                fixer = FlxExceptionFixer()
                new_tree = fixer.visit(tree)

                if fixer.changes and not args.dry_run:
                    new_content = ast.unparse(new_tree)
                    filepath.write_text(new_content)

                file_changes.extend(fixer.changes)
            except Exception as e:
                print(f"  Error with AST fixes: {e}")

        if args.type in {"methods", "all"}:
            if not args.dry_run:
                method_changes = fix_method_references(filepath)
                file_changes.extend(method_changes)
            else:
                print("  Would fix method references")

        if args.type in {"constructors", "all"}:
            if not args.dry_run:
                constructor_changes = fix_constructor_calls(filepath, inventory)
                file_changes.extend(constructor_changes)
            else:
                print("  Would fix constructor calls")

        if file_changes:
            total_changes += len(file_changes)
            for change in file_changes:
                if change["type"] == "import_function":
                    print(f"  Import: {change['old']} -> {change['new']}")
                elif change["type"] == "add_import":
                    print(f"  Added import: {change['import']}")
                elif change["type"] == "exception_attr":
                    print(f"  Exception: {change['old']} -> {change['new']}")
                elif change["type"] == "method_reference":
                    print(f"  Method: {change['old']} -> {change['new']}")
                elif change["type"] == "constructor_arg":
                    print(
                        f"  Constructor: {change['class']} added {change['arg']}={change['value']}"
                    )
        else:
            print("  No changes needed")

    print(f"\nTotal changes: {total_changes}")

    if args.dry_run:
        print("\nThis was a dry run. Use without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
