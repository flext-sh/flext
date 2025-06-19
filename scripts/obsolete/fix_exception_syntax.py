#!/usr/bin/env python3
"""Fix exception handling syntax errors in Python files.

This script specifically fixes issues with duplicate "from e" clauses in raise statements,
which cause syntax errors.

Usage:
    python flx_exception_syntax.py [--dry-run]
"""

import argparse
import re
import sys
from pathlib import Path


class ExceptionSyntaxFixer:
    """Fix exception handling syntax issues in Python files."""

    def __init__(self, dry_run=False) -> None:
        """Initialize the fixer.

        Args:
            dry_run: If True, don't actually modify files, just report issues

        """
        self.dry_run = dry_run
        self.files_modified = 0
        self.fixes_count = 0

    def process_directory(self, directory) -> None:
        """Process all Python files in a directory recursively.

        Args:
            directory: Path to directory to process

        """
        for file_path in directory.glob("**/*.py"):
            if ".venv" in str(file_path) or "__pycache__" in str(file_path):
                continue
            self.process_file(file_path)

    def process_file(self, file_path) -> None:
        """Process a single Python file.

        Args:
            file_path: Path to file to process

        """
        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Fix multiple "from e" clauses in raise statements
            content = self._fix_multiple_from_clauses(content)

            if content != original_content:
                self.files_modified += 1
                print(f"Fixing exception syntax in {file_path}")
                if not self.dry_run:
                    file_path.write_text(content, encoding="utf-8")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _fix_multiple_from_clauses(self, content) -> None:
        """Fix multiple "from x" clauses in raise statements.

        Args:
            content: File content to fix

        Returns:
            Fixed content

        """
        # Pattern to find raise statements with multiple "from e" clauses
        pattern = r"(raise\s+[a-zA-Z_][a-zA-Z0-9_.]*\(.*?\)\s+from\s+[a-zA-Z_][a-zA-Z0-9_]*)(\s+from\s+[a-zA-Z_][a-zA-Z0-9_]*)+\s*"

        # Function to replace multiple "from e" with just one
        def replace_multiple_from(match):
            # Keep only the first "from e" clause
            first_part = match.group(1)
            self.fixes_count += 1
            return first_part

        # Apply the fix
        re.sub(
            pattern,
            replace_multiple_from,
            content,
            flags=re.DOTALL,
        )

    def print_summary(self) -> None:
        """Print a summary of the fixes made."""
        print("\nSummary:")
        print(f"Files modified: {self.files_modified}")
        print(f"Exception syntax fixes: {self.fixes_count}")

        if self.dry_run:
            print("\nThis was a dry run. No files were actually modified.")


def main() -> None:
    """Run the script."""
    parser = argparse.ArgumentParser(description="Fix exception handling syntax issues")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't modify files, just report issues",
    )
    args = parser.parse_args()

    # Get the flx_project root directory
    project_root = Path(__file__).parent.parent / "dc-api-x"
    if not project_root.exists():
        project_root = Path(__file__).parent.parent  # Try parent directory

    src_dir = project_root / "src" / "dc_api_x"
    tests_dir = project_root / "tests"

    if not src_dir.exists():
        print(f"Source directory not found at {src_dir}")
        sys.exit(1)

    print(f"Processing dc-api-x flx_project at {project_root}")
    fixer = ExceptionSyntaxFixer(dry_run=args.dry_run)

    # Process source code
    fixer.process_directory(src_dir)

    # Process tests if they exist
    if tests_dir.exists():
        fixer.process_directory(tests_dir)

    fixer.print_summary()


if __name__ == "__main__":
    main()
