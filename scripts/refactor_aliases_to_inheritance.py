#!/usr/bin/env python3
"""Script to convert class aliases to real inheritance.

Converts patterns like:
    ClassName = Parent.ClassName
to:
    class ClassName(Parent.ClassName):
        \"\"\"ClassName - real inheritance.\"\"\"

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from re import Match

# Pattern to match class aliases: ClassName = Parent.ClassName
ALIAS_PATTERN = re.compile(
    r"^(\s*)([A-Z][a-zA-Z0-9_]*)\s*=\s*([A-Z][a-zA-Z0-9_]*\.[A-Z][a-zA-Z0-9_]*)\s*$",
)


def convert_alias_to_inheritance(match: Match[str]) -> str:
    """Convert alias to inheritance class."""
    indent = match.group(1)
    class_name = match.group(2)
    parent_class = match.group(3)

    return f'{indent}class {class_name}({parent_class}):\n{indent}    """{class_name} - real inheritance."""'


def process_file(filepath: Path) -> tuple[int, bool]:
    """Process a single file, converting aliases to inheritance.

    Returns:
        Tuple of (number of conversions, file_was_modified)

    """
    try:
        content = Path(filepath).read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return 0, False

    original_content = content
    lines = content.split("\n")
    modified_lines = []
    conversions = 0

    for i, line in enumerate(lines):
        match = ALIAS_PATTERN.match(line)
        if match:
            # Check if next line is a comment or docstring - preserve it
            next_line_idx = i + 1
            if next_line_idx < len(lines):
                next_line = lines[next_line_idx].strip()
                # If next line is already a docstring or comment, skip adding new docstring
                if next_line.startswith(('"""', "'''", "#")):
                    # Convert to inheritance but keep existing docstring
                    indent = match.group(1)
                    class_name = match.group(2)
                    parent_class = match.group(3)
                    modified_lines.append(
                        f"{indent}class {class_name}({parent_class}):",
                    )
                    conversions += 1
                    continue

            # Convert alias to inheritance with new docstring
            indent = match.group(1)
            class_name = match.group(2)
            parent_class = match.group(3)
            modified_lines.extend([
                f"{indent}class {class_name}({parent_class}):",
                f'{indent}    """{class_name} - real inheritance."""',
            ])
            conversions += 1
        else:
            modified_lines.append(line)

    if conversions > 0:
        new_content = "\n".join(modified_lines)
        if new_content != original_content:
            try:
                Path(filepath).write_text(new_content, encoding="utf-8")
                return conversions, True
            except Exception as e:
                print(f"Error writing {filepath}: {e}", file=sys.stderr)
                return conversions, False

    return conversions, False


def main() -> int:
    """Main entry point."""
    if len(sys.argv) > 1:
        target_files = [Path(p) for p in sys.argv[1:]]
    else:
        # Find all target files
        target_files = []
        target_names = {
            "models.py",
            "typings.py",
            "utilities.py",
            "constants.py",
            "protocols.py",
        }
        for root in Path().rglob("*"):
            if (
                "__pycache__" in str(root)
                or ".venv" in str(root)
                or ".git" in str(root)
            ):
                continue
            if root.name in target_names and (
                "src" in str(root) or "tests/helpers" in str(root)
            ):
                target_files.append(root)

    total_conversions = 0
    files_modified = 0

    for filepath in sorted(target_files):
        conversions, modified = process_file(filepath)
        if conversions > 0:
            print(f"{filepath}: {conversions} conversion(s)")
            total_conversions += conversions
            if modified:
                files_modified += 1

    print(f"\nTotal: {total_conversions} conversions in {files_modified} files")
    return 0 if total_conversions == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
