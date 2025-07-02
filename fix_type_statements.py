#!/usr/bin/env python3
"""Fix Python 3.12+ type statements to be compatible with Python 3.9+"""

import re
from pathlib import Path


def fix_type_statements_in_file(file_path: Path) -> bool:
    """Fix type statements in a single file. Returns True if changes were made."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Pattern to match "type VarName = Expression" at start of line (with optional whitespace)
        pattern = r"^(\s*)type\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$"

        def replace_type_statement(match):
            indent = match.group(1)
            var_name = match.group(2)
            expression = match.group(3)
            return f"{indent}{var_name} = {expression}"

        content = re.sub(pattern, replace_type_statement, content, flags=re.MULTILINE)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True

        return False

    except Exception:
        return False


def main():
    """Fix all Python files in the project."""
    root_path = Path(".")
    fixed_count = 0

    # Find all Python files, excluding .venv and legacy directories
    python_files = []

    for pattern in ["**/*.py"]:
        for file_path in root_path.glob(pattern):
            # Skip certain directories
            if any(
                part in file_path.parts for part in [".venv", "legacy", "__pycache__"]
            ):
                continue
            python_files.append(file_path)

    for file_path in python_files:
        if fix_type_statements_in_file(file_path):
            fixed_count += 1


if __name__ == "__main__":
    main()
