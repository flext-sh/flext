#!/usr/bin/env python3
"""Fix critical syntax errors - simple version."""

import os
import re
from pathlib import Path


def fix_file(file_path: str) -> bool:
    """Fix syntax errors in a single file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False

    original_content = content

    # Fix class inheritance with Union
    content = re.sub(r"class (\w+)\([^)]+, Union\):", r"class \1:", content)
    content = re.sub(r"class (\w+)\(Union\):", r"class \1:", content)

    # Fix logger with Union
    content = re.sub(r"logger = logging\.getLogger\([^)]+, Union\)",
                     r"logger = logging.getLogger(__name__)", content)

    # Fix broken imports
    content = re.sub(r", Union\)", r")", content)

    # Fix malformed function definitions
    content = re.sub(r'def (\w+)\(\s*"""TODO: Add docstring\."""\s*', r"def \1(", content)

    # Remove standalone Union parameters
    content = content.replace(", Union", "")
    content = content.replace("Union,", "")
    content = re.sub(r"\(Union\)", r"()", content)

    if content != original_content:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception:
            return False

    return False


def main():
    """Fix syntax errors in all projects."""
    projects = [
        "/home/marlonsc/flext/flext-tap-oracle-wms",
        "/home/marlonsc/flext/flext-target-oracle",
        "/home/marlonsc/flext/client-b-meltano-native"
    ]

    for project in projects:
        if not os.path.exists(project):
            continue

        print(f"🔧 Fixing {project}")
        python_files = list(Path(project).rglob("*.py"))
        fixed = 0

        for py_file in python_files:
            if fix_file(str(py_file)):
                fixed += 1

        print(f"  Fixed {fixed} files")


if __name__ == "__main__":
    main()
