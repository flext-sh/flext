#!/usr/bin/env python3
"""Script to fix missing return type annotations in test files."""

import re
import sys
from pathlib import Path


def find_test_files(directory: str) -> list[Path]:
    """Find all Python test files in the given directory and its subdirectories."""
    test_files = []
    for path in Path(directory).glob("**/*.py"):
        # Match common test file patterns
        if (
            path.name.startswith("test_")
            or path.name.endswith("_test.py")
            or "test" in path.parts
        ):
            test_files.append(path)
    return test_files


def flx_test_return_types(file_path: Path) -> int:
    """Add -> None return type annotations to test functions.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Pattern to match test functions without return type annotations
    test_func_pattern = re.compile(
        r"^(\s*)(def\s+(test_\w+)\s*\([^)]*\))(\s*:)", re.MULTILINE,
    )

    # Find all test functions and add return type annotations
    modified_content = content
    fixes_count = 0

    for match in test_func_pattern.finditer(content):
        indent, func_def, _func_name, colon = match.groups()
        full_match = match.group(0)

        # Skip if this function already has a return type annotation
        if "->" in func_def:
            continue

        # Modify the function definition to add -> None
        new_def = f"{indent}{func_def} -> None{colon}"
        modified_content = modified_content.replace(full_match, new_def, 1)
        fixes_count += 1

    # Also fix pytest fixture functions
    fixture_func_pattern = re.compile(
        r"^(\s*)(@pytest\.fixture(?:\([^)]*\))?)\s*\n\s*(def\s+\w+\s*\([^)]*\))(\s*:)",
        re.MULTILINE,
    )

    for match in fixture_func_pattern.finditer(content):
        indent, decorator, func_def, colon = match.groups()
        full_match = match.group(0)

        # Skip if this fixture already has a return type annotation
        if "->" in func_def:
            continue

        # Add a comment to help with manual annotation
        new_def = f"{indent}{decorator}\n{indent}{func_def} -> None{colon}  # TODO: Add proper return type if this fixture returns a value"
        modified_content = modified_content.replace(full_match, new_def, 1)
        fixes_count += 1

    # Write the modified content back if changes were made
    if fixes_count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)

    return fixes_count


def main() -> None:
    """Main function to process all test files in the specified directory."""
    if len(sys.argv) < 2:
        print("Usage: python flx_test_return_types.py <directory>")
        print("Example: python flx_test_return_types.py ./tests")
        sys.exit(1)

    directory = sys.argv[1]

    # Get all test files
    test_files = find_test_files(directory)

    # Track statistics
    total_fixes = 0
    files_modified = 0

    # Process each file
    for file_path in test_files:
        fixes = fix_test_return_types(file_path)

        if fixes > 0:
            files_modified += 1
            total_fixes += fixes
            print(f"Fixed {file_path}: {fixes} functions updated")

    # Print summary
    print("\nSummary:")
    print(f"Test files processed: {len(test_files)}")
    print(f"Files modified: {files_modified}")
    print(f"Total functions fixed: {total_fixes}")


if __name__ == "__main__":
    main()
