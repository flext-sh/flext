#!/usr/bin/env python3
"""Script to fix specific mypy errors in dc-api-x codebase."""

import os
import subprocess
import sys


def flx_mypy_issues(file_path: str) -> None:
    """Fix specific issues in Python files."""
    # Read the file line by line
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Process the file line by line
    new_lines: list = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Fix 1: Fix "offset[Any]" -> "offset"
        if "offset[Any]" in line:
            line = line.replace("offset[Any]", "offset")

        # Fix 2: Fix dict[str, Any] default factory
        if "default_factory=dict[str, Any]" in line:
            line = line.replace(
                "default_factory=dict[str, Any]",
                "default_factory=dict",
            )

        # Fix 3: Fix the to_paginate_options method return
        if "result = PaginateOptions(" in line:
            line = line.replace("result = ", "return ")

        # Fix 4: Remove blocks with "if self is not None:" or "if doctyper is
        # not None:"
        if (
            "if self is not None:" in line.strip()
            or "if doctyper is not None:" in line.strip()
        ):
            # Skip this entire block
            indent_level = len(line) - len(line.lstrip())
            i += 1

            # Skip until we find a line with same or less indentation
            while i < len(lines) and (
                not lines[i].strip()
                or len(lines[i]) - len(lines[i].lstrip()) > indent_level
            ):
                i += 1

            continue

        # Fix 5: Remove "else: # Handle None case appropriately" blocks
        if "else:" in line.strip() and "Handle None case appropriately" in line:
            # Skip this line and next line (pass)
            i += 2
            continue

        # Fix 6: Remove assert isinstance statements with PaginateOptions
        if (
            'assert isinstance(result, "PaginateOptions")' in line
            or "assert isinstance(result," in line
        ):
            # Skip this line and the next (return result)
            i += 2
            continue

        # Fix 7: Fix lines with multi-line parameters that have wrong
        # indentation
        if ": Annotated[" in line:
            # This might be part of a parameter definition
            next_line_idx = i + 1
            if (
                next_line_idx < len(lines)
                and "doctyper.Option" in lines[next_line_idx]
                and lines[next_line_idx].lstrip().startswith("doctyper")
            ):
                # Fix indentation if needed
                if (
                    len(lines[next_line_idx]) - len(lines[next_line_idx].lstrip())
                    < len(line) - len(line.lstrip()) + 4
                ):
                    # Indentation is incorrect, fix it
                    expected_indent = " " * (len(line) - len(line.lstrip()) + 4)
                    lines[next_line_idx] = (
                        expected_indent + lines[next_line_idx].lstrip()
                    )

        # Add the processed line
        new_lines.append(line)
        i += 1

    # Look for missing Optional import
    needs_optional = False
    for line in new_lines:
        if (
            "Optional[" in line
            and "from typing import Optional, Optional"
            not in "".join(
                new_lines,
            )
        ):
            needs_optional = True
            break

    if needs_optional:
        for i, line in enumerate(new_lines):
            if "from typing import Optional, " in line and "Optional" not in line:
                if "Union" in line:
                    new_lines[i] = line.replace("Union", "Optional, Union")
                    new_lines[i] = line.rstrip() + ", Optional\n"
                break

    # Write the processed lines back to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def find_files_with_pattern(directory: str, pattern: str) -> list[str]:
    """Find files containing a specific pattern."""
    try:
        result = subprocess.run(
            f"find {directory} -type f -name '*.py' -print | xargs grep -l '{pattern}'",
            shell=True,
            capture_output=True,
            text=True,
            check=False,
        )
        files = result.stdout.strip().split("\n")
        return [f for f in files if f]  # Filter out empty lines
    except Exception as e:
        print(f"Error finding files: {e}")
        return []


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python flx_dcapix_complete.py <path_to_dc_api_x>")
        sys.exit(1)

    base_dir = sys.argv[1]

    # Find files with the specific issues
    print("Finding files with mypy issues...")
    files_with_offset_issue = find_files_with_pattern(base_dir, r"offset\[Any\]")
    print(f"Found {len(files_with_offset_issue)} files with offset[Any] issues")

    # Process each file
    for file_path in files_with_offset_issue:
        print(f"Fixing issues in {file_path}...")
        fix_mypy_issues(file_path)

    # Also fix base.py directly since it's known to have issues
    base_py_path = os.path.join(base_dir, "src", "dc_api_x", "entity", "base.py")
    if os.path.exists(base_py_path) and base_py_path not in files_with_offset_issue:
        print(f"Fixing issues in {base_py_path}...")
        fix_mypy_issues(base_py_path)

    print("Done.")
