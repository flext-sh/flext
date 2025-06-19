#!/usr/bin/env python3
"""Final validation script to ensure zero tolerance for duplications."""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from pathlib import Path


def find_class_duplications() -> bool:
    """Find any duplicate class names or similar functionality."""
    # Track all adapter classes
    adapter_classes: defaultdict[str, list[str]] = defaultdict(list)
    base_classes: defaultdict[str, list[str]] = defaultdict(list)

    src_dir = Path("src/flx")
    if not src_dir.exists():
        return False

    for py_file in src_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    file_path = str(py_file)

                    # Check for adapter classes
                    if "adapter" in class_name.lower():
                        adapter_classes[class_name].append(file_path)

                    # Check for base classes
                    if "base" in class_name.lower() or class_name.endswith("Mixin"):
                        base_classes[class_name].append(file_path)

        except Exception:
            pass

    # Report findings
    violations = 0

    duplicate_adapters = {
        name: files for name, files in adapter_classes.items() if len(files) > 1
    }
    if duplicate_adapters:
        for class_name, files in duplicate_adapters.items():
            for file_path in files:
                pass
            violations += 1

    for _name, files in sorted(adapter_classes.items()):
        pass

    duplicate_bases = {
        name: files for name, files in base_classes.items() if len(files) > 1
    }
    if duplicate_bases:
        for class_name, files in duplicate_bases.items():
            for file_path in files:
                pass
            violations += 1

    for _name, files in sorted(base_classes.items()):
        if len(files) == 1:  # Only show non-duplicates
            pass

    # Check for dead code patterns
    dead_code_patterns = [
        "*_production_engine.py",
        "*_standardized.py",
        "*_extended.py",
        "*_legacy.py",
        "*_old.py",
        "*_backup.py",
        "*_template.py",
    ]

    dead_files: list[str] = []
    for pattern in dead_code_patterns:
        dead_files.extend(str(dead_file) for dead_file in src_dir.rglob(pattern))

    if dead_files:
        for file_path in dead_files:
            violations += 1

    # Final assessment
    return violations == 0


def check_standardization() -> bool:
    """Check that all adapters follow standardization patterns."""
    adapter_files: list[str] = []
    src_dir = Path("src/flx/adapters")

    if src_dir.exists():
        adapter_files.extend(
            str(py_file)
            for py_file in src_dir.rglob("*.py")
            if py_file.name != "__init__.py" and "mixin" not in py_file.name.lower()
        )

    compliance_issues = 0

    for adapter_file in adapter_files:
        try:
            with open(adapter_file, encoding="utf-8") as f:
                content = f.read()

            # Check for required patterns
            required_patterns = [
                "EnhancedAdapter",
                "get_default_config",
                "_get_specific_operations",
                "_perform_health_check_operation",
                "# Configuration fields organized hierarchically",
            ]

            missing_patterns = [
                pattern for pattern in required_patterns if pattern not in content
            ]

            if missing_patterns:
                for _pattern in missing_patterns:
                    pass
                compliance_issues += 1

        except Exception:
            compliance_issues += 1

    return compliance_issues == 0


if __name__ == "__main__":
    success1 = find_class_duplications()
    success2 = check_standardization()

    if success1 and success2:
        sys.exit(0)
    else:
        sys.exit(1)
