#!/usr/bin/env python3
"""Main script to run all mypy error fixers in the right order."""

import subprocess
import sys
from pathlib import Path


def run_command(command: list[str]) -> tuple[int, str]:
    """Run a command and return the return code and output."""
    process = subprocess.run(command, capture_output=True, text=True, check=False)
    return process.returncode, process.stdout + process.stderr


def count_mypy_errors(directory: str) -> int:
    """Run mypy and count the number of errors."""
    _returncode, output = run_command(["mypy", directory])

    # Count errors by counting the number of lines containing "error:"
    error_count = output.count("error:")

    print(f"Found {error_count} mypy errors in {directory}")
    return error_count


def flx_errors(directory: str) -> None:
    """Run all the fixers in the right order."""
    # First, run mypy to get a baseline count
    initial_errors = count_mypy_errors(directory)

    if initial_errors == 0:
        print("No mypy errors found! The codebase is already clean.")
        return

    # Step 1: Fix test functions first (simplest case)
    print("\n=== Step 1: Fixing test function return types ===")
    _returncode, output = run_command(["python", "flx_test_return_types.py", directory])
    print(output)

    # Re-run mypy to see the progress
    current_errors = count_mypy_errors(directory)
    print(
        f"Reduced errors from {initial_errors} to {current_errors} ({
            initial_errors - current_errors
        } fixed)",
    )

    # Step 2: Fix missing return type annotations for non-test functions
    print("\n=== Step 2: Fixing missing return type annotations ===")
    _returncode, output = run_command(
        ["python", "flx_mypy_errors.py", directory, "return_type"],
    )
    print(output)

    # Re-run mypy to see the progress
    previous_errors = current_errors
    current_errors = count_mypy_errors(directory)
    print(
        f"Reduced errors from {previous_errors} to {current_errors} ({
            previous_errors - current_errors
        } fixed)",
    )

    # Step 3: Fix missing type parameters for generic types
    print("\n=== Step 3: Fixing missing type parameters for generic types ===")
    _returncode, output = run_command(
        ["python", "flx_generic_type_params.py", directory],
    )
    print(output)

    # Re-run mypy to see the progress
    previous_errors = current_errors
    current_errors = count_mypy_errors(directory)
    print(
        f"Reduced errors from {previous_errors} to {current_errors} ({
            previous_errors - current_errors
        } fixed)",
    )

    # Step 4: Remove unused type ignore comments
    print("\n=== Step 4: Removing unused type ignore comments ===")
    _returncode, output = run_command(
        ["python", "flx_mypy_errors.py", directory, "unused_ignores"],
    )
    print(output)

    # Re-run mypy to see the progress
    previous_errors = current_errors
    current_errors = count_mypy_errors(directory)
    print(
        f"Reduced errors from {previous_errors} to {current_errors} ({
            previous_errors - current_errors
        } fixed)",
    )

    # Step 5: Apply advanced fixes (more complex issues)
    print("\n=== Step 5: Applying advanced fixes ===")
    _returncode, output = run_command(
        ["python", "flx_advanced_mypy_errors.py", directory],
    )
    print(output)

    # Final mypy run to see the overall progress
    final_errors = count_mypy_errors(directory)

    # Print summary
    print("\n=== Summary ===")
    print(f"Initial mypy errors: {initial_errors}")
    print(f"Remaining mypy errors: {final_errors}")
    print(
        f"Total fixed: {initial_errors - final_errors} ({
            (initial_errors - final_errors) / initial_errors * 100:.1f
        }%)",
    )

    if final_errors > 0:
        print("\nRemaining errors require manual intervention. Common patterns to fix:")
        print("1. Check functions that return values and add specific return types")
        print(
            "2. Add proper None checks before accessing attributes of optional values",
        )
        print(
            "3. Fix incompatible return types by ensuring function returns match the declared type",
        )
        print(
            "4. Fix assignment issues by ensuring variable types are compatible with assigned values",
        )
        print("5. Address abstract class issues by implementing required methods")
        print("6. Fix call argument issues by matching function signatures")
        print("7. Fix attribute errors by ensuring attributes exist on the objects")


def main() -> None:
    """Main function to fix all mypy errors in the specified directory."""
    if len(sys.argv) < 2:
        print("Usage: python flx_all_mypy_errors.py <directory>")
        print("Example: python flx_all_mypy_errors.py ./src")
        sys.exit(1)

    directory = sys.argv[1]

    # Check if mypy is installed
    returncode, _output = run_command(["mypy", "--version"])
    if returncode != 0:
        print("Error: mypy is not installed or not in the PATH.")
        print("Please install mypy with: pip install mypy")
        sys.exit(1)

    # Check if the necessary scripts exist
    required_scripts = [
        "fix_test_return_types.py",
        "fix_mypy_errors.py",
        "fix_generic_type_params.py",
        "fix_advanced_mypy_errors.py",
    ]

    missing_scripts = [
        script for script in required_scripts if not Path(script).exists()
    ]
    if missing_scripts:
        print("Error: The following required scripts are missing:")
        for script in missing_scripts:
            print(f"  - {script}")
        print("Please make sure all the fixer scripts are in the current directory.")
        sys.exit(1)

    # Run the fixers
    fix_errors(directory)


if __name__ == "__main__":
    main()
