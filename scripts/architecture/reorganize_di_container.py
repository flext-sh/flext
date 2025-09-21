#!/usr/bin/env python3
"""Fix DI container ordering issues in FLEXT API files.

This script fixes issues where DI container functions are called before import,
and removes duplicate initialization comments.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import re
import sys
from pathlib import Path


def fix_di_ordering(file_path: Path) -> bool:
    """Fix DI container ordering in a Python file.

    Args:
      file_path: Path to the Python file to fix

    Returns:
      True if file was modified, False otherwise

    """
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Fix calls to DI functions before import
        content = re.sub(
            r"(from typing import.*?\n)\n([^#\n]*?get_\w+\(\).*?\n)+\n"
            r"(# Use centralized|from flext_)",
            r"\1\n\3",
            content,
            flags=re.MULTILINE,
        )

        # Remove duplicate "Initialize types via DI container" comments
        content = re.sub(
            r"(# Initialize types via DI container\n.*?\n)\n"
            r"# Initialize types via DI container\n",
            r"\1",
            content,
            flags=re.MULTILINE,
        )

        # Clean up multiple blank lines
        content = re.sub(r"\n{3,}", "\n\n", content)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True

    except (OSError, ValueError, TypeError):
        return False

    return False


def main() -> None:
    """Main function to fix DI ordering in all Python files."""
    base_dir = Path("/home/marlonsc/flext/flext-api")

    if not base_dir.exists():
        sys.exit(1)

    # Find all Python files with potential DI ordering issues
    python_files = list(base_dir.rglob("*.py"))

    files_fixed = 0
    for py_file in python_files:
        if fix_di_ordering(py_file):
            files_fixed += 1


if __name__ == "__main__":
    main()
