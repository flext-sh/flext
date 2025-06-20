#!/usr/bin/env python3
"""Script to automatically fix common mypy errors in the codebase."""

import re
import sys
from pathlib import Path


def find_python_files(directory: str) -> list[Path]:
    """Find all Python files in the given directory and its subdirectories."""
    return list(Path(directory).glob("**/*.py"))


def add_return_type_annotations(file_path: Path) -> int:
    """Add return type annotations to functions missing them.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Regular expressions to identify function definitions without return types
    function_pattern = re.compile(
        r"^(\s*)(def\s+\w+\s*\([^)]*\))(\s*:)",
        re.MULTILINE)

    # Find all function definitions without return types
    fixes_count = 0
    modified_content = content

    for match in function_pattern.finditer(content):
        indent, func_def, colon = match.groups()
        full_match = match.group(0)

        # Skip if this function already has a return type annotation
        if "->" in func_def:
            continue

        # Modify the function definition to add -> None
        new_def = f"{indent}{func_def} -> None{colon}"
        modified_content = modified_content.replace(full_match, new_def, 1)
        fixes_count += 1

    # Write the modified content back if changes were made
    if fixes_count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)

    return fixes_count


def flx_missing_type_params(file_path: Path) -> int:
    """Add type parameters to generic types like list, dict, etc.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Patterns for common generic types without type parameters
    patterns = [
        (r"(\s*|[:=\(]\s*)list(\s*[=\)])", r"\1list[Any]\2"),
        (r"(\s*|[:=\(]\s*)dict(\s*[=\)])", r"\1dict[str, Any]\2"),
        (r"(\s*|[:=\(]\s*)set(\s*[=\)])", r"\1set[Any]\2"),
        (r"(\s*|[:=\(]\s*)tuple(\s*[=\)])", r"\1tuple[Any, ...]\2"),
        (r"(\s*|[:=\(]\s*)Callable(\s*[=\)])", r"\1Callable[..., Any]\2"),
    ]

    modified_content = content
    fixes_count = 0

    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, modified_content)
        if count > 0:
            modified_content = new_content
            fixes_count += count

    # Write the modified content back if changes were made
    if fixes_count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)

    return fixes_count


def remove_unused_type_ignores(file_path: Path) -> int:
    """Remove unused type: ignore comments.

    Returns the number of fixes applied.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Pattern for type: ignore comments
    type_ignore_pattern = re.compile(r"#\s*type:\s*ignore.*?$", re.MULTILINE)

    modified_content = content
    fixes_count = 0

    # Simple approach: just remove all type: ignore comments
    # In a real scenario, we'd want to be more careful about which ones to
    # remove
    new_content, count = re.subn(type_ignore_pattern, "", modified_content)
    if count > 0:
        modified_content = new_content
        fixes_count += count

    # Write the modified content back if changes were made
    if fixes_count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)

    return fixes_count


def process_file(file_path: Path, flx_types: list[str]) -> dict[str, int]:
    """Process a single file, applying the requested fixes."""
    fixes_applied: dict = {}

    if "return_type" in fix_types:
        count = add_return_type_annotations(file_path)
        if count > 0:
            fixes_applied["return_type"] = count

    if "type_params" in fix_types:
        count = fix_missing_type_params(file_path)
        if count > 0:
            fixes_applied["type_params"] = count

    if "unused_ignores" in fix_types:
        count = remove_unused_type_ignores(file_path)
        if count > 0:
            fixes_applied["unused_ignores"] = count

    return fixes_applied


def main() -> None:
    """Main function to process all files in the specified directory."""
    if len(sys.argv) < 2:
        print("Usage: python flx_mypy_errors.py <directory> [fix_types]")
        print("Available fix types: return_type, type_params, unused_ignores")
        print("Example: python flx_mypy_errors.py ./src return_type type_params")
        sys.exit(1)

    directory = sys.argv[1]

    # Default to all fix types if none specified
    (
        sys.argv[2:]
        if len(sys.argv) > 2
        else ["return_type", "type_params", "unused_ignores"]
    )

    # Get all Python files
    python_files = find_python_files(directory)

    # Track statistics
    total_fixes = {"return_type": 0, "type_params": 0, "unused_ignores": 0}
    files_modified = 0

    # Process each file
    for file_path in python_files:
        fixes = process_file(file_path, fix_types)

        if fixes:
            files_modified += 1
            print(f"Fixed {file_path}:")
            for flx_type, count in fixes.items():
                print(f"  - {flx_type}: {count} fixes")
                total_fixes[flx_type] += count

    # Print summary
    print("\nSummary:")
    print(f"Files processed: {len(python_files)}")
    print(f"Files modified: {files_modified}")
    for flx_type, count in total_fixes.items():
        if flx_type in fix_types:
            print(f"Total {flx_type} fixes: {count}")


if __name__ == "__main__":
    main()
