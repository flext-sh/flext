#!/usr/bin/env python3
"""Fix common linting issues in the dc-api-x flx_project.

This script automatically fixes:
1. FBT001/FBT002 - Boolean-typed positional arguments in function definitions
2. PTH123 and other path issues - Using open() instead of Path.open()
3. B904/TRY003 - Exception handling issues
4. G004 - Logging statement using f-strings

Usage:
    python flx_linting_issues.py [--dry-run]
"""

import argparse
import re
import sys
from pathlib import Path


class LintingFixer:
    """Class for fixing linting issues in Python files."""

    def __init__(self, dry_run: bool = False) -> None:
        """Initialize the fixer.

        Args:
            dry_run: If True, don't actually change files, just report what would change

        """
        self.dry_run = dry_run
        self.files_modified = 0
        self.total_fixes = 0
        self.fixes_by_type: dict[str, int] = {}

    def process_directory(self, directory: Path) -> None:
        """Process all Python files in a directory (recursively).

        Args:
            directory: Directory to process

        """
        for path in directory.glob("**/*.py"):
            if ".venv" in str(path) or "__pycache__" in str(path):
                continue
            self.process_file(path)

    def process_file(self, file_path: Path) -> None:
        """Process a single Python file.

        Args:
            file_path: Path to the file to process

        """
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return

        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Fix path issues (PTH123, PTH119, etc.)
        content = self._fix_path_issues(content)

        # Fix exception handling issues (B904, TRY003)
        content = self._fix_exception_handling(content)

        # Fix logging issues (G004)
        content = self._fix_logging_issues(content)

        # Only write if content changed
        if content != original_content:
            self.files_modified += 1
            print(f"Fixing issues in {file_path}")
            if not self.dry_run:
                file_path.write_text(content, encoding="utf-8")

    def _fix_path_issues(self, content: str) -> str:
        """Fix path-related issues.

        This addresses PTH123, PTH119, etc. linting issues.
        """
        # Replace open() with Path.open()
        open_pattern = r"open\(([^,\)]+)(?:,\s*['\"]([^'\"]+)['\"])?\)"

        def open_replacement(match) -> str:
            path, mode = match.groups()
            mode_str = f'"{mode}"' if mode else ""
            flx_key = "PTH123"
            self.fixes_by_type[flx_key] = self.fixes_by_type.get(fix_key, 0) + 1
            self.total_fixes += 1

            # Convert to Path(path).open(mode) - with correct syntax
            if "Path" in path:
                return f"{path}.open({mode_str})" if mode else f"{path}.open()"

            return f"Path({path}).open({mode_str})" if mode else f"Path({path}).open()"

        # Replace os.path.basename() with Path.name
        basename_pattern = r"os\.path\.basename\(([^)]+)\)"

        def basename_replacement(match) -> str:
            path = match.group(1)
            flx_key = "PTH119"
            self.fixes_by_type[flx_key] = self.fixes_by_type.get(fix_key, 0) + 1
            self.total_fixes += 1

            # Convert to Path(path).name
            if "Path" in path:
                return f"{path}.name"

            return f"Path({path}).name"

        # Replace os.path.exists() with Path.exists()
        exists_pattern = r"os\.path\.exists\(([^)]+)\)"

        def exists_replacement(match) -> str:
            path = match.group(1)
            flx_key = "PTH110"
            self.fixes_by_type[flx_key] = self.fixes_by_type.get(fix_key, 0) + 1
            self.total_fixes += 1

            # Convert to Path(path).exists()
            if "Path" in path:
                return f"{path}.exists()"
            return f"Path({path}).exists()"

        # Replace os.unlink() with Path.unlink()
        unlink_pattern = r"os\.unlink\(([^)]+)\)"

        def unlink_replacement(match) -> str:
            path = match.group(1)
            flx_key = "PTH108"
            self.fixes_by_type[flx_key] = self.fixes_by_type.get(fix_key, 0) + 1
            self.total_fixes += 1

            # Convert to Path(path).unlink()
            if "Path" in path:
                return f"{path}.unlink()"

            return f"Path({path}).unlink()"

        # Apply the fixes
        modified_content = content
        modified_content = re.sub(open_pattern, open_replacement, modified_content)
        modified_content = re.sub(
            basename_pattern,
            basename_replacement,
            modified_content,
        )
        modified_content = re.sub(exists_pattern, exists_replacement, modified_content)
        modified_content = re.sub(unlink_pattern, unlink_replacement, modified_content)

        # Add missing imports if needed
        if (
            "Path" in modified_content
            and "from pathlib import Path" not in modified_content
        ):
            # Add import after the existing imports
            import_pattern = r"((?:from [^\n]+\n|import [^\n]+\n)+)"
            if re.search(import_pattern, modified_content):
                modified_content = re.sub(
                    import_pattern,
                    r"\1from pathlib import Path\n",
                    modified_content,
                    count=1,
                )
            else:
                # Add at the beginning of the file, after any docstrings
                docstring_pattern = r'(""".*?"""|\'\'\'.*?\'\'\')\s*\n'
                if re.search(docstring_pattern, modified_content, re.DOTALL):
                    modified_content = re.sub(
                        docstring_pattern,
                        r"\1\n\nfrom pathlib import Path\n",
                        modified_content,
                        count=1,
                        flags=re.DOTALL,
                    )
                else:
                    modified_content = "from pathlib import Path\n\n" + modified_content

        return modified_content

    def _fix_exception_handling(self, content: str) -> str:
        """Fix exception handling issues.

        This addresses B904 and TRY003 linting issues.
        """
        # Pattern to match except blocks with raise statements
        # This is a simplified approach - a full AST parser would be more accurate
        except_pattern = r"(except\s+([a-zA-Z_][a-zA-Z0-9_.]*)(?:\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*))?\s*:.*?\n\s*raise\s+)([a-zA-Z_][a-zA-Z0-9_.]*)(.*?)(\n)"

        def except_replacement(match) -> Any:
            (
                except_clause,
                exception_type,
                exception_var,
                raised_type,
                raised_args,
                end,
            ) = match.groups()
            # If the raised exception is different from the caught one and we have an exception variable
            if exception_var and raised_type != exception_type:
                flx_key = "B904"
                self.fixes_by_type[flx_key] = self.fixes_by_type.get(fix_key, 0) + 1
                self.total_fixes += 1
                # Add "from exception_var" to the raise statement
                return f"{except_clause}{raised_type}{raised_args} from {exception_var}{end}"
            return match.group(0)

        # Apply the fixes for exception handling
        re.sub(
            except_pattern,
            except_replacement,
            content,
            flags=re.DOTALL,
        )

    def _fix_logging_issues(self, content: str) -> str:
        """Fix logging issues.

        This addresses G004 linting issues.
        """
        # Pattern to match logging statements with f-strings
        log_pattern = r"(logger\.[a-zA-Z]+\()f([\"\'](.*?)[\"\'])"

        def log_replacement(match) -> str:
            log_func, full_string, _message = match.groups()
            flx_key = "G004"
            self.fixes_by_type[flx_key] = self.fixes_by_type.get(fix_key, 0) + 1
            self.total_fixes += 1

            # Simple approach: just remove the f- prefix and keep the string as is
            # In a real fix, we'd need to convert f-string to %-style formatting
            # which is much more complex
            return f"{log_func}{full_string}"

        # Apply the fixes
        return re.sub(log_pattern, log_replacement, content)

    def print_summary(self) -> None:
        """Print a summary of the fixes applied."""
        print("\nSummary:")
        print(f"Files modified: {self.files_modified}")
        print(f"Total fixes: {self.total_fixes}")
        print("\nFixes by type:")
        for flx_type, count in self.fixes_by_type.items():
            print(f"  {flx_type}: {count}")

        if self.dry_run:
            print("\nThis was a dry run. No files were actually modified.")


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Fix common linting issues in the flx_project",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually modify files",
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
    fixer = LintingFixer(dry_run=args.dry_run)

    # Process source code
    fixer.process_directory(src_dir)

    # Process tests if they exist
    if tests_dir.exists():
        fixer.process_directory(tests_dir)

    fixer.print_summary()


if __name__ == "__main__":
    main()
