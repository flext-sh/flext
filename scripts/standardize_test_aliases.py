#!/usr/bin/env python3
"""Standardize test helper aliases to tm, tt, tu, tc, tp pattern.

Converts:
- m = TestsModels -> tm = TestsModels
- t = TestsTypings -> tt = TestsTypings
- u = TestsUtilities -> tu = TestsUtilities
- c = TestsConstants -> tc = TestsConstants
- p = TestsProtocols -> tp = TestsProtocols
"""

import re
import sys
from pathlib import Path

REPLACEMENTS = [
    (r"\bm\s*=\s*TestsModels\b", "tm = TestsModels"),
    (r"\bt\s*=\s*TestsTypings\b", "tt = TestsTypings"),
    (r"\bt\s*=\s*TestsTypes\b", "tt = TestsTypes"),
    (r"\bu\s*=\s*TestsUtilities\b", "tu = TestsUtilities"),
    (r"\bc\s*=\s*TestsConstants\b", "tc = TestsConstants"),
    (r"\bp\s*=\s*TestsProtocols\b", "tp = TestsProtocols"),
]


def fix_file(filepath: Path) -> tuple[int, bool]:
    """Fix aliases in a file.

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

    for pattern, replacement in REPLACEMENTS:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            fixes += 1

    # Handle __all__ exports
    content = content.replace('"m"', '"tm"')
    content = content.replace('"t"', '"tt"')
    content = content.replace('"u"', '"tu"')
    content = content.replace('"c"', '"tc"')
    content = content.replace('"p"', '"tp"')

    if content != original_content:
        try:
            with Path(filepath).open("w", encoding="utf-8") as f:
                f.write(content)
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
        # Find all test helper files
        target_files = []
        target_names = {
            "models.py",
            "typings.py",
            "utilities.py",
            "constants.py",
            "protocols.py",
            "__init__.py",
        }
        for root in Path().rglob("*"):
            if (
                "__pycache__" in str(root)
                or ".venv" in str(root)
                or ".git" in str(root)
            ):
                continue
            if root.name in target_names and "tests/helpers" in str(root):
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
