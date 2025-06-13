#!/usr/bin/env python3
"""Fix duplicate star (*) separators in function definitions.

This script identifies and fixes functions where we accidentally introduced
multiple * separators in function parameter lists, which is a syntax error.

Usage:
    python flx_duplicate_stars.py [--dry-run]
"""

import argparse
import re
import sys
from pathlib import Path


class StarSeparatorFixer:
    """Fix duplicate * separators in function parameter lists."""

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

            # Fix function definitions with duplicate * separators
            content = self._fix_duplicate_stars(content)

            if content != original_content:
                self.files_modified += 1
                print(f"Fixing duplicate * separators in {file_path}")
                if not self.dry_run:
                    file_path.write_text(content, encoding="utf-8")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _fix_duplicate_stars(self, content):
        """Fix function definitions with duplicate * separators.

        Args:
            content: File content to fix

        Returns:
            Fixed content

        """
        # Split content into lines for easier processing
        lines = content.split("\n")

        # Check each line for duplicate * separators
        for i in range(len(lines)):
            # Look for patterns like "*, *, arg" or similar
            if re.search(r"\*,\s*\*,", lines[i]):
                # Replace with a single *
                lines[i] = re.sub(r"\*,\s*\*,", "*, ", lines[i])
                self.fixes_count += 1

            # Also check for leading * with space followed by * at the beginning of parameters
            if re.search(r"^\s+\*,\s*\*\s+", lines[i]):
                lines[i] = re.sub(
                    r"^\s+\*,\s*\*\s+",
                    lambda m: m.group(0).replace("*, *", "*"),
                    lines[i],
                )
                self.fixes_count += 1

            # Fix any self, *, * patterns
            if re.search(r"self,\s*\*,\s*\*", lines[i]):
                lines[i] = re.sub(r"self,\s*\*,\s*\*", "self, *", lines[i])
                self.fixes_count += 1

            # Fix any connection, *, * patterns
            if re.search(r"connection:\s*Any,\s*\*,\s*\*", lines[i]):
                lines[i] = re.sub(
                    r"connection:\s*Any,\s*\*,\s*\*", "connection: Any, *", lines[i],
                )
                self.fixes_count += 1

            # Fix to_dict with duplicate stars
            if re.search(r"def\s+to_dict\(self,\s*\*,\s*\*", lines[i]):
                lines[i] = re.sub(
                    r"def\s+to_dict\(self,\s*\*,\s*\*", "def to_dict(self, *", lines[i],
                )
                self.fixes_count += 1

            # Fix def __init__ with duplicate stars
            if re.search(r"self,\s*\*,\s*\*\s+success", lines[i]):
                lines[i] = re.sub(
                    r"self,\s*\*,\s*\*\s+success", "self, * success", lines[i],
                )
                self.fixes_count += 1

        return "\n".join(lines)

    def print_summary(self) -> None:
        """Print a summary of the fixes made."""
        print("\nSummary:")
        print(f"Files modified: {self.files_modified}")
        print(f"Star separator fixes: {self.fixes_count}")

        if self.dry_run:
            print("\nThis was a dry run. No files were actually modified.")


def main() -> None:
    """Run the script."""
    parser = argparse.ArgumentParser(
        description="Fix duplicate * separators in function definitions",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Don't modify files, just report issues",
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
    fixer = StarSeparatorFixer(dry_run=args.dry_run)

    # Process source code
    fixer.process_directory(src_dir)

    # Process tests if they exist
    if tests_dir.exists():
        fixer.process_directory(tests_dir)

    fixer.print_summary()


if __name__ == "__main__":
    main()
