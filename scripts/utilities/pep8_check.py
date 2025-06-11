#!/usr/bin/env python3
"""
PEP 8 Compliance Checker.

This script checks if Python code files follow PEP 8 standards by:
1. Checking formatting with Black
2. Checking import sorting with isort
3. Linting with Ruff

Usage:
    python pep8_check.py [path1] [path2] ...
    If no paths are provided, uses the current directory.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_python_files(directory: Path) -> list[Path]:
    """
    Find all Python files in a directory recursively.

    Args:
        directory: The directory to search.

    Returns:
        A list of paths to Python files.
    """
    return list(directory.glob("**/*.py"))


def run_command(command: list[str], description: str) -> tuple[bool, str]:
    """
    Run a command with subprocess and capture output.

    Args:
        command: Command to run as a list of strings.
        description: Description of the command for output.

    Returns:
        A tuple of (success_flag, output_string)
    """
    print(f"Running {description}...")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def check_black(files: list[Path]) -> tuple[bool, str]:
    """
    Check if files are formatted correctly with Black.

    Args:
        files: list of file paths to check.

    Returns:
        A tuple of (formatted_correctly, output_message)
    """
    if not files:
        return True, "No files to check"

    str_files = [str(f) for f in files]
    # Black returns 0 if files are formatted correctly
    return run_command(["black", "--check"] + str_files, "Black check")


def check_isort(files: list[Path]) -> tuple[bool, str]:
    """
    Check if imports are sorted correctly with isort.

    Args:
        files: list of file paths to check.

    Returns:
        A tuple of (sorted_correctly, output_message)
    """
    if not files:
        return True, "No files to check"

    str_files = [str(f) for f in files]
    # isort returns 0 if imports are sorted correctly
    return run_command(["isort", "--check"] + str_files, "isort check")


def check_ruff(files: list[Path]) -> tuple[bool, str]:
    """
    Check for linting issues with Ruff.

    Args:
        files: list of file paths to check.

    Returns:
        A tuple of (no_issues, output_message)
    """
    if not files:
        return True, "No files to check"

    str_files = [str(f) for f in files]
    # Ruff returns 0 if there are no issues
    return run_command(["ruff", "check"] + str_files, "Ruff check")


def main(paths: list[str] | None = None) -> int:
    """
    Main function to check PEP 8 standards.

    Args:
        paths: list of paths to process. If None, uses current directory.

    Returns:
        Exit code (0 for success, 1 for errors).
    """
    if paths is None or not paths:
        paths = [os.getcwd()]

    all_files = []
    for path_str in paths:
        path = Path(path_str)
        if path.is_dir():
            all_files.extend(find_python_files(path))
        elif path.is_file() and path.suffix == ".py":
            all_files.append(path)
        else:
            print(f"Skipping {path} (not a Python file or directory)")

    print(f"Found {len(all_files)} Python files to check")

    # Check tools in sequence
    all_passed = True
    black_passed, black_output = check_black(all_files)
    isort_passed, isort_output = check_isort(all_files)
    ruff_passed, ruff_output = check_ruff(all_files)

    # Print results
    print("\n" + "=" * 50)
    print("PEP 8 Compliance Check Results:")
    print("=" * 50)

    print(f"\nBlack formatting: {'✅ PASSED' if black_passed else '❌ FAILED'}")
    if not black_passed:
        print("Issues found:")
        print(black_output)

    print(f"\nisort imports: {'✅ PASSED' if isort_passed else '❌ FAILED'}")
    if not isort_passed:
        print("Issues found:")
        print(isort_output)

    print(f"\nRuff linting: {'✅ PASSED' if ruff_passed else '❌ FAILED'}")
    if not ruff_passed:
        print("Issues found:")
        print(ruff_output)

    all_passed = black_passed and isort_passed and ruff_passed

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All PEP 8 checks passed! Code complies with standards.")
        return 0
    print("❌ Some PEP 8 checks failed. See details above.")
    print("Run `make pep8` to automatically fix these issues.")
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check PEP 8 standards in Python code.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Paths to files or directories to check.",
    )
    args = parser.parse_args()

    sys.exit(main(args.paths))
