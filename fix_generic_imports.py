#!/usr/bin/env python3
"""
Fix missing Generic imports in the converted files.
"""

import re
from pathlib import Path


def find_files_needing_generic() -> list[Path]:
    """Find files that use Generic[T] but don't import Generic."""
    files = []
    legacy_path = Path("/home/marlonsc/flext/legacy")

    for py_file in legacy_path.rglob("*.py"):
        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            # Check if file uses Generic[...] syntax
            if re.search(r"Generic\[", content):
                # Check if Generic is imported
                if not re.search(r"from typing import.*Generic", content):
                    files.append(py_file)
        except Exception:
            continue

    return files


def fix_generic_import(file_path: Path) -> bool:
    """Add Generic import to a file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Find existing typing import and add Generic
        typing_pattern = r"from typing import ([^#\n]+)"
        match = re.search(typing_pattern, content)

        if match:
            existing_imports = match.group(1).strip()
            if "Generic" not in existing_imports:
                new_imports = existing_imports + ", Generic"
                content = re.sub(
                    typing_pattern, f"from typing import {new_imports}", content
                )

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return True

        return False
    except Exception:
        return False


def main():
    """Main function."""
    files = find_files_needing_generic()

    if not files:
        return

    fixed_count = 0
    for file_path in files:
        if fix_generic_import(file_path):
            fixed_count += 1
        else:
            pass


if __name__ == "__main__":
    main()
