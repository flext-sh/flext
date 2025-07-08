#!/usr/bin/env python3
"""Script to fix line break issues in TOML files where multiple statements are on the same line."""

import re
from pathlib import Path


def fix_line_breaks(file_path: Path) -> bool:
    """Fix TOML files where multiple statements are merged on the same line."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix patterns like: ]keyword = [
        content = re.sub(r"(\][^=\n]*)([\w\-]+\s*=)", r"\1\n\2", content)

        # Fix patterns like: "keyword = ["
        content = re.sub(r'(")[a-zA-Z_\-]+\s*=\s*\[', lambda m: m.group(0).replace('"', '"\n'), content)

        # Fix patterns where ] is followed by a keyword without newline
        content = re.sub(r"(\])\s*([a-zA-Z_\-]+\s*=)", r"\1\n\2", content)

        # Fix patterns where } is followed by a keyword without newline
        content = re.sub(r"(\})\s*([a-zA-Z_\-]+\s*=)", r"\1\n\2", content)

        # Fix extra quotes at end of lines after fixing structure
        content = re.sub(r'(=\s*"[^"]*")"\s*$', r"\1", content, flags=re.MULTILINE)
        content = re.sub(r'(=\s*\[[^\]]*\])"\s*$', r"\1", content, flags=re.MULTILINE)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        print(f"No changes needed: {file_path}")
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main() -> None:
    """Fix line break issues in all pyproject.toml files."""
    base_dir = Path("/home/marlonsc/flext")

    # Only process project files, not .venv
    toml_files = [toml_file for toml_file in base_dir.rglob("pyproject.toml") if ".venv" not in str(toml_file)]

    print(f"Found {len(toml_files)} project pyproject.toml files")

    fixed_count = 0
    for toml_file in toml_files:
        if fix_line_breaks(toml_file):
            fixed_count += 1

    print(f"\nFixed line breaks in {fixed_count} files")


if __name__ == "__main__":
    main()
