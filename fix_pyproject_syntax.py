#!/usr/bin/env python3
"""Script to fix TOML syntax errors in all pyproject.toml files.
Removes extra quotes that cause TOML parsing errors.
"""

import re
from pathlib import Path


def fix_toml_quotes(file_path: Path) -> bool:
    """Fix common TOML syntax errors by removing extra quotes."""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        original_lines = lines[:]
        fixed_lines = []

        for line in lines:
            fixed_line = line

            # Pattern 1: requires = ["something"]" (extra quote at end)
            fixed_line = re.sub(r'(=\s*\[.*?\])"\s*$', r"\1", fixed_line)

            # Pattern 2: key = "value"" (extra quote at end of simple values)
            fixed_line = re.sub(r'(=\s*"[^"]*")"\s*$', r"\1", fixed_line)

            # Pattern 3: "item"," in arrays (extra quote before comma)
            fixed_line = re.sub(r'"([^"]*)",\"', r'"\1",', fixed_line)

            # Pattern 4: version = "1.0""
            fixed_line = re.sub(r'(version\s*=\s*"[^"]*")"\s*$', r"\1", fixed_line)

            # Pattern 5: array items ending with ","
            fixed_line = re.sub(r'(\s*"[^"]*"),\"', r'\1",', fixed_line)

            fixed_lines.append(fixed_line)

        if fixed_lines != original_lines:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(fixed_lines)
            print(f"Fixed: {file_path}")
            return True
        print(f"No changes needed: {file_path}")
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main() -> None:
    """Find and fix all pyproject.toml files in the workspace."""
    base_dir = Path("/home/marlonsc/flext")

    # Find all pyproject.toml files
    toml_files = list(base_dir.rglob("pyproject.toml"))

    print(f"Found {len(toml_files)} pyproject.toml files")

    fixed_count = 0
    for toml_file in toml_files:
        if fix_toml_quotes(toml_file):
            fixed_count += 1

    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
