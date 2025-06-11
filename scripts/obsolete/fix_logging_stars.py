#!/usr/bin/env python3
"""
Fix star separator issues in the utils/logging.py file.

This script specifically fixes the issue with multiple keyword-only parameter markers
in the setup_logger function of the utils/logging.py file.

Usage:
    python fix_logging_stars.py
"""

from pathlib import Path


def fix_logging_stars():
    """Fix the duplicate star separators in the logging.py file."""
    # Path to the logging.py file
    file_path = (
        Path(__file__).parent.parent
        / "dc-api-x"
        / "src"
        / "dc_api_x"
        / "utils"
        / "logging.py"
    )

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    # Read the file content
    content = file_path.read_text(encoding="utf-8")

    # The issue is in lines 20-22 with two * separators
    # We need to keep only one * separator and merge the two parameter groups

    # Original pattern:
    # *,  console: bool = True,
    # *, structured: bool = False,

    # Replace pattern with a fixed version
    fixed_content = content.replace(
        "*,  console: bool = True,\n    *, structured: bool = False,",
        "*,  console: bool = True, structured: bool = False,",
    )

    # Only write if content changed
    if fixed_content != content:
        file_path.write_text(fixed_content, encoding="utf-8")
        print(f"Fixed star separator issues in {file_path}")
    else:
        print("No changes needed")


if __name__ == "__main__":
    fix_logging_stars()
