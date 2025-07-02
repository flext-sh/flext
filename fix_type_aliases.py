#!/usr/bin/env python3
"""
Fix Python 3.12+ type alias syntax in legacy/ directory.

Converts type Foo = Bar to Foo = Bar (Python 3.9+ compatible)
"""

import re
import subprocess
from pathlib import Path


def find_files_with_type_aliases() -> list[Path]:
    """Find all Python files with type alias syntax."""
    try:
        result = subprocess.run(
            [
                "find",
                "/home/marlonsc/flext/legacy",
                "-name",
                "*.py",
                "-exec",
                "grep",
                "-l",
                "type .*=",
                "{}",
                ";",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            return [
                Path(line.strip())
                for line in result.stdout.splitlines()
                if line.strip()
            ]
        return []
    except Exception:
        return []


def fix_type_aliases(file_path: Path) -> bool:
    """Fix type alias syntax in a file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Pattern for type aliases: type Name = Value
        # Match type aliases, but not type comments or other uses
        pattern = r"^(\s*)type\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)$"

        def replace_type_alias(match):
            indent = match.group(1)
            name = match.group(2)
            value = match.group(3)
            return f"{indent}{name} = {value}"

        # Apply the replacement
        content = re.sub(pattern, replace_type_alias, content, flags=re.MULTILINE)

        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False
    except Exception:
        return False


def main():
    """Main function."""
    files = find_files_with_type_aliases()

    if not files:
        return

    fixed_count = 0
    for file_path in files:
        if fix_type_aliases(file_path):
            fixed_count += 1


if __name__ == "__main__":
    main()
