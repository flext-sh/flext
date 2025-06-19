#!/usr/bin/env python3
"""Run all linting issue fixers in sequence.

This script runs all of the individual fixing scripts in the appropriate order
to address various linting issues in the dc-api-x flx_project.

Usage:
    python flx_all_issues.py [--dry-run]
"""

import argparse
import subprocess
from pathlib import Path


def run_fixer_script(script_name, dry_run=False) -> Any:
    """Run a fixer script with the appropriate arguments.

    Args:
        script_name: Name of the script to run
        dry_run: Whether to run in dry-run mode

    Returns:
        Process return code

    """
    script_path = Path(__file__).parent / script_name

    if not script_path.exists():
        print(f"Script not found: {script_path}")
        return 1

    # Build command
    cmd = ["python", str(script_path)]
    if dry_run and script_name not in {
        "fix_logging_stars.py",
        "fix_syntax_errors.py",
        "fix_client_star_separator.py",
        "fix_undefined_names.py",
        "fix_remaining_syntax_errors.py",
    }:
        cmd.append("--dry-run")

    # Run script
    print(f"\n=== Running {script_name} ===")
    result = subprocess.run(cmd, capture_output=False, text=True, check=True)

    return result.returncode


def main() -> None:
    """Run all fixer scripts in sequence."""
    parser = argparse.ArgumentParser(description="Run all linting issue fixers")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't modify files, just report issues",
    )
    args = parser.parse_args()

    # list of fixer scripts to run in order
    fixer_scripts = [
        "flx_linting_issues.py",  # Path issues, exception issues, logging format issues
        "flx_duplicate_stars.py",  # Fix duplicated * separators in function parameters
        "flx_exception_syntax.py",  # Fix multiple "from e" clauses in exception handling
        "flx_logging_stars.py",  # Fix duplicate star separator in logging.py
        "flx_syntax_errors.py",  # Fix malformed raise statements and function definitions
        "flx_client_star_separator.py",  # Fix the star separator in client.py
        "flx_undefined_names.py",  # Fix undefined name 'e' errors in client.py
        "flx_remaining_syntax_errors.py",  # Fix remaining syntax errors in client.py and adapters.py
    ]

    # Run each fixer script
    for script in fixer_scripts:
        return_code = run_fixer_script(script, args.dry_run)
        if return_code != 0:
            print(f"Error running {script}. Return code: {return_code}")

    print("\n=== All fixer scripts completed ===")
    print("Run 'make lint' to check if there are any remaining issues.")


if __name__ == "__main__":
    main()
