#!/usr/bin/env python3
"""Fix duplicate Protocol inheritance in protocols.py files.

Removes duplicate Protocol from classes that inherit from another Protocol.
Example: class XProtocol(Parent.Protocol, Protocol): -> class XProtocol(Parent.Protocol):
"""

import re
import sys
from pathlib import Path
from re import Match

# Pattern to match: class XProtocol(Parent.Protocol, Protocol):
# Handles both single line and multi-line with decorator
PATTERN = re.compile(
    r"(\s*@runtime_checkable\s*\n)?(\s*)class\s+(\w+Protocol)\s*\(([^,)]+Protocol),\s*Protocol\):",
    re.MULTILINE,
)


def fix_file(filepath: Path) -> tuple[int, bool]:
    """Fix duplicate Protocol inheritance in a file.

    Returns:
        Tuple of (number of fixes, file_was_modified)

    """
    try:
        with Path(filepath).open("r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return 0, False

    original_content = content
    fixes = 0

    # Replace pattern: class XProtocol(Parent.Protocol, Protocol): -> class XProtocol(Parent.Protocol):
    def replace(match: Match[str]) -> str:
        nonlocal fixes
        fixes += 1
        decorator = match.group(1) or ""
        indent = match.group(2)
        class_name = match.group(3)
        parent = match.group(4)
        return f"{decorator}{indent}class {class_name}({parent}):"

    new_content = PATTERN.sub(replace, content)

    if new_content != original_content:
        try:
            with Path(filepath).open("w", encoding="utf-8") as f:
                f.write(new_content)
            return fixes, True
        except Exception as e:
            print(f"Error writing {filepath}: {e}", file=sys.stderr)
            return fixes, False

    return fixes, False


def main() -> int:
    """Main entry point."""
    if len(sys.argv) > 1:
        target_files = [Path(p) for p in sys.argv[1:]]
    else:
        # Find all protocols.py files
        target_files = []
        for root in Path().rglob("protocols.py"):
            if (
                "__pycache__" in str(root)
                or ".venv" in str(root)
                or ".git" in str(root)
            ):
                continue
            if "src" in str(root):
                target_files.append(root)

    total_fixes = 0
    files_modified = 0

    for filepath in sorted(target_files):
        fixes, modified = fix_file(filepath)
        if fixes > 0:
            print(f"{filepath}: {fixes} fix(es)")
            total_fixes += fixes
            if modified:
                files_modified += 1

    print(f"\nTotal: {total_fixes} fixes in {files_modified} files")
    return 0 if total_fixes == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
