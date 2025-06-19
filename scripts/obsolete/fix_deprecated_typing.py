#!/usr/bin/env python3
"""Script to fix deprecated typing imports in Python files.
Replaces typing.list, typing.dict, etc. with their modern equivalents.
"""

import re
import sys
from pathlib import Path


def find_python_files(directory: str) -> list[Path]:
    """Find all Python files in the given directory and its subdirectories."""
    return list(Path(directory).glob("**/*.py"))


def flx_deprecated_typing(file_path: Path) -> dict[str, int]:
    """Fix deprecated typing imports in a Python file.

    Returns a dictionary with counts of fixes by type.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Check if file has any deprecated typing imports
    if "from typing import " not in content:
        return {}

    # Get the original typing import line
    typing_import_match = re.search(
        r"from typing import (.*?)(?:\n|$)", content, re.MULTILINE
    )
    if not typing_import_match:
        return {}

    original_imports = typing_import_match.group(1).strip()
    import_line = typing_import_match.group(0).strip()

    # Define the deprecated types to replace
    replacements = {
        "list": "list",
        "dict": "dict",
        "Set": "set",
        "tuple": "tuple",
        "Optional": "Optional",  # Keep this for now
        "Union": "Union",  # Keep this for now
        "Any": "Any",  # Keep this
        "TypeVar": "TypeVar",  # Keep this
        "Callable": "Callable",  # Keep this
    }

    # Track changes
    changes = {}
    new_imports = []

    # Process each import
    for imp in re.split(r",\s*", original_imports):
        imp = imp.strip()
        if imp in replacements:
            # If it's a deprecated type that needs replacement
            if imp in {"list", "dict", "Set", "tuple"}:
                changes[imp] = changes.get(imp, 0) + 1
                # Don't add to new imports as we'll use the builtin types
            else:
                # Keep other imports from typing that aren't deprecated
                new_imports.append(imp)
        else:
            # Keep any other imports we don't recognize
            new_imports.append(imp)

    if not changes:
        return {}  # No changes to make

    # Create new import line if there are still typing imports needed
    if new_imports:
        new_import_line = f"from typing import {', '.join(new_imports)}"
    else:
        new_import_line = ""  # No more typing imports needed

    # Replace the import line
    if new_import_line:
        modified_content = content.replace(import_line, new_import_line)
    else:
        # Remove the entire line if no imports remain
        modified_content = content.replace(import_line + "\n", "")
        if modified_content == content:  # If there was no newline
            modified_content = content.replace(import_line, "")

    # Replace the actual type uses in the code
    for old_type, new_type in replacements.items():
        if old_type in {"list", "dict", "Set", "tuple"} and old_type in changes:
            # Replace patterns like list[int] with list[int]
            pattern = r"\b" + re.escape(old_type) + r"\["
            replacement = new_type + "["
            modified_content, count = re.subn(pattern, replacement, modified_content)
            if count > 0:
                changes[f"{old_type}_usage"] = count

    # Write the modified content back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(modified_content)

    return changes


def process_files(files: list[Path]) -> dict[str, int]:
    """Process multiple files and collect statistics."""
    total_changes = {}
    files_modified = 0

    for file_path in files:
        changes = fix_deprecated_typing(file_path)

        if changes:
            files_modified += 1
            print(f"Fixed {file_path}:")
            for change_type, count in changes.items():
                print(f"  - {change_type}: {count} replacements")
                total_changes[change_type] = total_changes.get(change_type, 0) + count

    return {
        "files_modified": files_modified,
        "changes": total_changes,
    }


def main() -> None:
    """Main function to fix deprecated typing imports in all Python files."""
    if len(sys.argv) < 2:
        print(
            "Usage: python flx_deprecated_typing.py <directory_or_file> [directory_or_file2 ...]"
        )
        print("Example: python flx_deprecated_typing.py ./src ./tests")
        sys.exit(1)

    # Get all files to process
    all_files = []
    for path_arg in sys.argv[1:]:
        path = Path(path_arg)
        if path.is_file() and path.suffix == ".py":
            all_files.append(path)
        elif path.is_dir():
            all_files.extend(find_python_files(str(path)))

    if not all_files:
        print("No Python files found in the specified paths.")
        sys.exit(1)

    print(f"Found {len(all_files)} Python files to process.")

    # Process all files
    results = process_files(all_files)

    # Print summary
    print("\n=== Summary ===")
    print(f"Files processed: {len(all_files)}")
    print(f"Files modified: {results['files_modified']}")

    if results["changes"]:
        print("\nReplacements made:")
        for change_type, count in results["changes"].items():
            print(f"  - {change_type}: {count}")
    else:
        print("\nNo deprecated typing imports found.")


if __name__ == "__main__":
    main()
