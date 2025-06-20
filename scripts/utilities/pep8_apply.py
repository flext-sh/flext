#!/usr/bin/env python3
"""PEP 8 Compliance Script.

This script applies PEP 8 standards to Python code files by:
1. Formatting with Black
2. Sorting imports with isort
3. Fixing issues with Ruff

Usage:
    python pep8_apply.py [path1] [path2] ...
    If no paths are provided, uses the current directory.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_python_files(directory: Path) -> list[Path]:
    """Find all Python files in a directory recursively.

    Args:
        directory: The directory to search.

    Returns:
        A list of paths to Python files.

    """
    return list(directory.glob("**/*.py"))


def run_command(command: list[str], description: str) -> bool:
    """Run a command with subprocess and handle errors.

    Args:
        command: Command to run as a list of strings.
        description: Description of the command for output.

    Returns:
        True if the command was successful, False otherwise.

    """
    print(f"Running {description}...")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"{description} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {description}:")
        print(e.stderr)
        return False


def apply_black(files: list[Path]) -> bool:
    """Format files with Black.

    Args:
        files: list of file paths to format.

    Returns:
        True if formatting was successful, False otherwise.

    """
    if not files:
        return True

    str_files = [str(f) for f in files]
    return run_command(["black", *str_files], "Black formatter")


def apply_isort(files: list[Path]) -> bool:
    """Sort imports with isort.

    Args:
        files: list of file paths to sort imports in.

    Returns:
        True if sorting was successful, False otherwise.

    """
    if not files:
        return True

    str_files = [str(f) for f in files]
    return run_command(["isort", *str_files], "isort import sorter")


def apply_ruff(files: list[Path]) -> bool:
    """Fix issues with Ruff.

    Args:
        files: list of file paths to fix.

    Returns:
        True if fixing was successful, False otherwise.

    """
    if not files:
        return True

    str_files = [str(f) for f in files]
    return run_command(["ruff", "check", "--fix", *str_files], "Ruff linter")


def main(paths: list[str] | None = None) -> int:
    """Main function to apply PEP 8 standards.

    Args:
        paths: list of paths to process. If None, uses current directory.

    Returns:
        Exit code (0 for success, 1 for errors).

    """
    if paths is None or not paths:
        paths = [os.getcwd()]

    all_files: list = []
    for path_str in paths:
        path = Path(path_str)
        if path.is_dir():
            all_files.extend(find_python_files(path))
        elif path.is_file() and path.suffix == ".py":
            all_files.append(path)
            print(f"Skipping {path} (not a Python file or directory)")

    print(f"Found {len(all_files)} Python files to process")

    # Apply tools in sequence
    success = True
    success = success and apply_ruff(all_files)
    success = success and apply_black(all_files)
    success = success and apply_isort(all_files)

    if success:
        print("All PEP 8 standards applied successfully!")
        return 0
    print("There were errors applying PEP 8 standards.")
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Apply PEP 8 standards to Python code.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Paths to files or directories to process.",
    )
    args = parser.parse_args()

    sys.exit(main(args.paths))
