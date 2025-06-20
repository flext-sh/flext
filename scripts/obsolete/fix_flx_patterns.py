#!/usr/bin/env python3
"""Fix common patterns in FLX codebase based on mypy error analysis."""

import ast
import re
from pathlib import Path


class FlxPatternFixer(ast.NodeTransformer):
    """Fix common FLX patterns using AST transformation."""

    def __init__(self) -> None:
        self.changes: list[dict[str, any]] = []
        self.current_class: str | None = None
        self.imported_classes: set[str] = set()

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Track current class."""
        old_class = self.current_class
        self.current_class = node.name
        result = self.generic_visit(node)
        self.current_class = old_class
        return result

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Fix import statements."""
        # Fix imports like: from module import ClassName -> from module import
        # FlxClassName
        new_names: list = []
        changed = False

        for alias in node.names:
            name = alias.name
            asname = alias.asname

            # Check common patterns that need Flx prefix
            needs_flx = any(
                [
                    name in {
                        "AsyncPluginManager",
                        "PluggableAsyncEventPublisher"},
                    name.endswith("EventProcessor") and not name.startswith("Flx"),
                    name.endswith("EventFilter") and not name.startswith("Flx"),
                    name.endswith("EventTransformer") and not name.startswith("Flx"),
                    name.endswith("Broker") and not name.startswith("Flx"),
                    name.endswith("Middleware") and not name.startswith("Flx"),
                    name.endswith("Handler") and not name.startswith("Flx"),
                    name.endswith("Tracker") and not name.startswith("Flx"),
                    name in {
                        "EndpointInfo",
                        "ComponentType",
                        "ShutdownPhase",
                        "ShutdownMetrics",
                        "ComponentShutdownEvent",
                        "ShutdownReport",
                        "LogMessage",
                        "TraceId",
                        "LogSeverity",
                        "BaseUrlBuilder",
                    },
                ])

            if needs_flx and not name.startswith("Flx"):
                new_name = f"Flx{name}"
                new_alias = ast.alias(name=new_name, asname=asname or name)
                new_names.append(new_alias)
                changed = True
                self.changes.append(
                    {
                        "type": "import",
                        "old": name,
                        "new": new_name,
                        "line": node.lineno,
                    }
                )
                if asname:
                    self.imported_classes.add(asname)
                    self.imported_classes.add(name)
                new_names.append(alias)
                if asname:
                    self.imported_classes.add(asname)
                    self.imported_classes.add(name)

        if changed:
            node.names = new_names

        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Fix class name references."""
        name = node.id

        # Skip if already imported with old name
        if name in self.imported_classes:
            return node

        # Check if this name needs Flx prefix
        needs_flx = any(
            [
                name in {
                    "AsyncPluginManager",
                    "PluggableAsyncEventPublisher"},
                name.endswith("EventProcessor") and not name.startswith("Flx"),
                name.endswith("EventFilter") and not name.startswith("Flx"),
                name.endswith("EventTransformer") and not name.startswith("Flx"),
                name.endswith("Broker") and not name.startswith("Flx"),
                name.endswith("Middleware") and not name.startswith("Flx"),
                name.endswith("Handler") and not name.startswith("Flx"),
                name.endswith("Tracker") and not name.startswith("Flx"),
                name in {
                    "EndpointInfo",
                    "ComponentType",
                    "ShutdownPhase",
                    "ShutdownMetrics",
                    "ComponentShutdownEvent",
                    "ShutdownReport",
                    "LogMessage",
                    "TraceId",
                    "LogSeverity",
                    "BaseUrlBuilder",
                    "InMemoryBroker",
                    "LoggingBrokerMiddleware",
                    "RetryBrokerMiddleware",
                    "BasicAnalyticsHandler",
                    "PerformanceTracker",
                    "LogAlertHandler",
                    "ConsoleAlertHandler",
                    "LoggingEventProcessor",
                    "DebugEventFilter",
                    "NoOpEventTransformer",
                    "ShutdownMetricsCollector",
                    "ComponentShutdownTimer",
                },
            ])

        if needs_flx and not name.startswith("Flx"):
            new_name = f"Flx{name}"
            node.id = new_name
            self.changes.append(
                {
                    "type": "name",
                    "old": name,
                    "new": new_name,
                    "line": node.lineno if hasattr(node, "lineno") else 0,
                }
            )

        return node

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Fix method calls."""
        node = self.generic_visit(node)

        if isinstance(node.func, ast.Attribute):
            attr = node.func.attr

            # Fix method calls that should have flx_ prefix
            if (
                not attr.startswith("flx_")
                and not attr.startswith("_")
                and attr
                not in {"__init__", "__str__", "__repr__", "__eq__", "__hash__"}
            ):
                # Check if it's a method that needs flx_ prefix
                needs_flx = False

                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "self"
                ):
                    if self.current_class and self.current_class.startswith(
                            "Flx"):
                        # Common methods that need flx_ prefix
                        if attr in {
                            "validate_url",
                            "discover_api_structure",
                            "publish_event",
                            "publish_events",
                            "format_and_display",
                            "record_event",
                            "get_metrics",
                            "numeric_value",
                            "full_path",
                        }:
                            needs_flx = True

                if needs_flx:
                    new_attr = f"flx_{attr}"
                    node.func.attr = new_attr
                    self.changes.append({"type": "method",
                                         "old": attr,
                                         "new": new_attr,
                                         "line": node.lineno if hasattr(node,
                                                                        "lineno") else 0,
                                         })

        return node


def fix_specific_patterns(filepath: Path) -> list[dict[str, any]]:
    """Fix specific patterns in a file."""
    changes: list = []
    try:
        content = filepath.read_text()
        original_content = content

        # Pattern 1: Fix function imports missing flx_ prefix
        patterns = [
            (
                r"from (flx\.plugins\.hookspecs\.\w+) import (register_\w+)",
                lambda m: f"from {m.group(1)} import flx_{m.group(2)}",
            ),
            # Pattern 2: Fix method names in module attributes
            (
                r'has no attribute "(register_\w+)"; maybe "flx_\1"',
                lambda m: f"flx_{m.group(1)}",
            ),
            # Pattern 3: Fix scan_object references
            (r"\bscan_object\b", "flx_scan_object"),
            # Pattern 4: Fix Exception attributes
            (r"exception\._context\b", 'getattr(exception, "_context", None)'),
            (r"exception\._details\b", 'getattr(exception, "_details", None)'),
            (r"exception\._error_chain\b",
             'getattr(exception, "_error_chain", None)'),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes.append(
                    {
                        "type": "regex",
                        "pattern": pattern,
                        "file": str(filepath),
                    }
                )
                content = new_content

        if content != original_content:
            filepath.write_text(content)

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

    return changes


def fix_file_ast(filepath: Path) -> list[dict[str, any]]:
    """Fix patterns using AST transformation."""
    try:
        content = filepath.read_text()
        tree = ast.parse(content)

        fixer = FlxPatternFixer()
        new_tree = fixer.visit(tree)

        if fixer.changes:
            new_content = ast.unparse(new_tree)
            filepath.write_text(new_content)

        return fixer.changes

    except Exception as e:
        print(f"Error processing {filepath} with AST: {e}")
        return []


def main() -> None:
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix FLX patterns")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed"
    )
    parser.add_argument("--file", help="Fix specific file only")
    args = parser.parse_args()

    src_dir = Path("/home/marlonsc/pyauto/flx/src")

    # Files with known issues
    problem_files = [
        "flx/infra/endpoints/url_builder.py",
        "flx/infra/endpoints/protocols.py",
        "flx/infra/logging/shutdown_metrics.py",
        "flx/infra/logging/domain.py",
        "flx/plugins/events.py",
        "flx/plugins/broker.py",
        "flx/plugins/analytics_.py",
        "flx/plugins/hookspecs/__init__.py",
        "flx/infra/async/pluggable_publisher.py",
        "flx/infra/async/__init__.py",
        "flx/infra/exceptions/helpers.py",
        "flx/infra/discovery/base.py",
        "flx/infra/output.py",
    ]

    if args.file:
        files = [Path(args.file)]
        files = [src_dir / f for f in problem_files if (src_dir / f).exists()]

    print(f"Processing {len(files)} files...")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLYING FIXES'}")

    total_changes = 0
    for filepath in files:
        print(f"\n{filepath.relative_to(src_dir.parent)}:")

        if args.dry_run:
            # Just analyze, don't change
            try:
                content = filepath.read_text()
                tree = ast.parse(content)
                fixer = FlxPatternFixer()
                fixer.visit(tree)
                changes = fixer.changes
            except Exception:
                changes: list = []
            # Apply AST fixes
            changes = fix_file_ast(filepath)
            # Apply regex fixes
            regex_changes = fix_specific_patterns(filepath)
            changes.extend(regex_changes)

        if changes:
            total_changes += len(changes)
            for change in changes:
                if change["type"] == "import":
                    print(
                        f"  Line {change['line']}: Import {change['old']} -> {change['new']}"
                    )
                elif change["type"] == "name":
                    print(
                        f"  Line {change['line']}: Name {change['old']} -> {change['new']}"
                    )
                elif change["type"] == "method":
                    print(
                        f"  Line {change['line']}: Method {change['old']} -> {change['new']}"
                    )
                elif change["type"] == "regex":
                    print(f"  Regex pattern: {change['pattern']}")
            print("  No changes needed")

    print(f"\nTotal changes: {total_changes}")

    if args.dry_run:
        print("\nThis was a dry run. Use without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
