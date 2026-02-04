#!/usr/bin/env python3
"""FLEXT Namespace Fix Script.

Validates and fixes namespace violations across FLEXT projects with:
- validate: Check current namespace violations
- dry-run: Preview changes WITHOUT modifying files
- exec: Apply with backup + ruff check + automatic module-by-module rollback

Usage:
    python /tmp/namespace_fix.py validate [--project PROJECT]
    python /tmp/namespace_fix.py dry-run [--project PROJECT]
    python /tmp/namespace_fix.py exec [--project PROJECT]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

# Configuration
FLEXT_ROOT = Path("/home/marlonsc/flext")

PROJECTS = [
    "flext-core",
    "flext-cli",
    "flext-ldif",
    "flext-ldap",
    "client-a-oud-mig",
]

# Timeout for ruff commands  # CONFIG
RUFF_TIMEOUT = 30


@dataclass
class Violation:
    """Represents a namespace violation."""

    file: Path
    line_number: int
    line_content: str
    pattern_name: str
    description: str


@dataclass
class FixResult:
    """Result of fixing a single file."""

    file: Path
    violations_found: int
    violations_fixed: int
    backup_path: Path | None = None
    ruff_passed: bool = True
    rolled_back: bool = False
    error: str | None = None


@dataclass
class ProjectResult:
    """Result of fixing an entire project."""

    project: str
    files_processed: int = 0
    files_modified: int = 0
    files_rolled_back: int = 0
    total_violations: int = 0
    total_fixed: int = 0
    file_results: list[FixResult] = field(default_factory=list)


class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"


class Logger:
    """Logging utilities."""

    @staticmethod
    def info(msg: str) -> None:
        """Print info message."""
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

    @staticmethod
    def success(msg: str) -> None:
        """Print success message."""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {msg}")

    @staticmethod
    def warning(msg: str) -> None:
        """Print warning message."""
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {msg}")

    @staticmethod
    def error(msg: str) -> None:
        """Print error message."""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")

    @staticmethod
    def dry_run(msg: str) -> None:
        """Print dry-run message."""
        print(f"{Colors.CYAN}[DRY-RUN]{Colors.NC} {msg}")


class NamespacePatterns:
    """Namespace violation patterns to detect and fix."""

    # Pattern: (regex, replacement_func or str, description)
    # INTENTIONAL CAST - These are pattern definitions for the fixer tool
    PATTERNS: ClassVar[list[tuple[re.Pattern[str], str | None, str]]] = [
        # typing.cast removal  # INTENTIONAL CAST
        (
            re.compile(r"from typing import .*\bcast\b"),
            None,  # Manual fix required
            "Remove typing.cast import - use proper types",  # INTENTIONAL CAST
        ),
        # Old typing patterns - replacement definitions  # INTENTIONAL CAST
        (
            re.compile(r"\bOptional\[([^\]]+)\]"),  # INTENTIONAL CAST
            r"\1 | None",  # INTENTIONAL CAST
            "Replace Optional with union None",  # INTENTIONAL CAST
        ),
        (
            re.compile(r"\bUnion\[([^,\]]+),\s*([^\]]+)\]"),  # INTENTIONAL CAST
            r"\1 | \2",  # INTENTIONAL CAST
            "Replace Union with pipe operator",  # INTENTIONAL CAST
        ),
        (
            re.compile(r"(?<![a-zA-Z])Dict\["),
            "dict[",
            "Replace Dict with dict",
        ),
        (
            re.compile(r"(?<![a-zA-Z])List\["),
            "list[",
            "Replace List with list",
        ),
        (
            re.compile(r"(?<![a-zA-Z])Tuple\["),
            "tuple[",
            "Replace Tuple with tuple",
        ),
        (
            re.compile(r"(?<![a-zA-Z])Set\["),
            "set[",
            "Replace Set with set",
        ),
    ]


class RuffValidator:
    """Ruff validation utilities."""

    @staticmethod
    def count_errors(file_path: Path) -> int:
        """Count ruff errors for a file."""
        try:
            result = subprocess.run(
                [
                    "/usr/bin/env",
                    "ruff",
                    "check",
                    "--output-format=json",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                timeout=RUFF_TIMEOUT,
                check=False,
            )
            if result.returncode == 0:
                return 0
            try:
                errors = json.loads(result.stdout)
                return len(errors)
            except json.JSONDecodeError:
                return result.stdout.count("\n")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return 0

    @staticmethod
    def check_file(file_path: Path) -> tuple[bool, str]:
        """Run ruff check on a file, return (passed, output)."""
        try:
            result = subprocess.run(
                ["/usr/bin/env", "ruff", "check", str(file_path)],
                capture_output=True,
                text=True,
                timeout=RUFF_TIMEOUT,
                check=False,
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Timeout running ruff"
        except FileNotFoundError:
            return True, "ruff not found, skipping"


class FileManager:
    """File operations with backup and restore."""

    @staticmethod
    def get_python_files(project_path: Path) -> list[Path]:
        """Get all Python files in a project's src directory."""
        src_dir = project_path / "src"
        if not src_dir.exists():
            return []
        return sorted(src_dir.rglob("*.py"))

    @staticmethod
    def create_backup(file_path: Path) -> Path:
        """Create a timestamped backup of a file."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_dir = FLEXT_ROOT / ".backups" / "namespace_fix" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)

        relative_path = file_path.relative_to(FLEXT_ROOT)
        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(file_path, backup_path)
        return backup_path

    @staticmethod
    def restore_backup(file_path: Path, backup_path: Path) -> bool:
        """Restore a file from backup."""
        try:
            shutil.copy2(backup_path, file_path)
            return True
        except OSError as e:
            Logger.error(f"Failed to restore {file_path}: {e}")
            return False


class ViolationFinder:
    """Find namespace violations in files."""

    @staticmethod
    def find_violations(file_path: Path) -> list[Violation]:
        """Find all namespace violations in a file."""
        violations: list[Violation] = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            Logger.warning(f"Cannot read {file_path}: {e}")
            return violations

        lines = content.splitlines()

        for regex, _replacement, description in NamespacePatterns.PATTERNS:
            for line_num, line in enumerate(lines, start=1):
                if regex.search(line):
                    violations.append(
                        Violation(
                            file=file_path,
                            line_number=line_num,
                            line_content=line.strip()[:80],
                            pattern_name=regex.pattern[:30],
                            description=description,
                        )
                    )

        return violations


class ViolationFixer:
    """Apply fixes to files."""

    @staticmethod
    def apply_fixes(file_path: Path, *, dry_run: bool = False) -> tuple[str, int]:
        """Apply all fixes to a file, return (new_content, fixes_applied)."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            Logger.error(f"Cannot read {file_path}: {e}")
            return "", 0

        original_content = content
        fixes_applied = 0

        for regex, replacement, description in NamespacePatterns.PATTERNS:
            if replacement is None:
                continue  # Skip patterns that need manual fix

            matches = len(regex.findall(content))
            if matches > 0:
                if dry_run:
                    Logger.dry_run(f"  Would fix {matches}x: {description}")
                else:
                    content = regex.sub(replacement, content)
                    fixes_applied += matches

        if content != original_content:
            return content, fixes_applied
        return content, 0


class ProjectProcessor:
    """Process projects for validation and fixing."""

    def __init__(self) -> None:
        """Initialize the project processor."""
        self.file_manager = FileManager()
        self.violation_finder = ViolationFinder()
        self.violation_fixer = ViolationFixer()
        self.ruff_validator = RuffValidator()

    def validate_project(self, project: str) -> ProjectResult:
        """Validate a project for namespace violations."""
        project_path = FLEXT_ROOT / project
        result = ProjectResult(project=project)

        if not project_path.exists():
            Logger.warning(f"Project {project} not found at {project_path}")
            return result

        Logger.info(f"Validating {project}...")
        python_files = self.file_manager.get_python_files(project_path)

        for file_path in python_files:
            violations = self.violation_finder.find_violations(file_path)
            if violations:
                result.files_processed += 1
                result.total_violations += len(violations)

                print(f"\n  {file_path.relative_to(FLEXT_ROOT)}:")
                for v in violations:
                    print(f"    L{v.line_number}: {v.description}")
                    print(f"         {v.line_content}")

        return result

    def dry_run_project(self, project: str) -> ProjectResult:
        """Dry-run fixes for a project."""
        project_path = FLEXT_ROOT / project
        result = ProjectResult(project=project)

        if not project_path.exists():
            Logger.warning(f"Project {project} not found at {project_path}")
            return result

        Logger.dry_run(f"Previewing fixes for {project}...")
        python_files = self.file_manager.get_python_files(project_path)

        for file_path in python_files:
            violations = self.violation_finder.find_violations(file_path)
            if violations:
                result.files_processed += 1
                result.total_violations += len(violations)

                print(f"\n  {file_path.relative_to(FLEXT_ROOT)}:")
                _, fixes = self.violation_fixer.apply_fixes(file_path)
                if fixes > 0:
                    result.files_modified += 1
                    result.total_fixed += fixes

        return result

    def exec_project(self, project: str) -> ProjectResult:
        """Execute fixes for a project with backup and rollback."""
        project_path = FLEXT_ROOT / project
        result = ProjectResult(project=project)

        if not project_path.exists():
            Logger.warning(f"Project {project} not found at {project_path}")
            return result

        Logger.info(f"Executing fixes for {project}...")
        python_files = self.file_manager.get_python_files(project_path)

        for file_path in python_files:
            violations = self.violation_finder.find_violations(file_path)
            if not violations:
                continue

            result.files_processed += 1
            result.total_violations += len(violations)

            # Get baseline ruff errors
            baseline_errors = self.ruff_validator.count_errors(file_path)

            # Create backup
            backup_path = self.file_manager.create_backup(file_path)

            # Apply fixes
            new_content, fixes_applied = self.violation_fixer.apply_fixes(
                file_path, dry_run=False
            )

            if fixes_applied == 0:
                continue

            # Write changes
            try:
                file_path.write_text(new_content, encoding="utf-8")
            except OSError as e:
                Logger.error(f"Failed to write {file_path}: {e}")
                result.file_results.append(
                    FixResult(
                        file=file_path,
                        violations_found=len(violations),
                        violations_fixed=0,
                        backup_path=backup_path,
                        error=str(e),
                    )
                )
                continue

            # Validate with ruff
            new_errors = self.ruff_validator.count_errors(file_path)

            if new_errors > baseline_errors:
                # Rollback
                Logger.warning(
                    f"  Rollback {file_path.name}: ruff errors increased "
                    f"({baseline_errors} -> {new_errors})"
                )
                self.file_manager.restore_backup(file_path, backup_path)
                result.files_rolled_back += 1
                result.file_results.append(
                    FixResult(
                        file=file_path,
                        violations_found=len(violations),
                        violations_fixed=0,
                        backup_path=backup_path,
                        ruff_passed=False,
                        rolled_back=True,
                    )
                )
            else:
                # Success
                result.files_modified += 1
                result.total_fixed += fixes_applied
                Logger.success(
                    f"  Fixed {file_path.name}: {fixes_applied} fixes applied"
                )
                result.file_results.append(
                    FixResult(
                        file=file_path,
                        violations_found=len(violations),
                        violations_fixed=fixes_applied,
                        backup_path=backup_path,
                        ruff_passed=True,
                    )
                )

        return result


class SummaryPrinter:
    """Print summary of results."""

    @staticmethod
    def print_summary(results: list[ProjectResult], mode: str) -> None:
        """Print summary of all results."""
        print(f"\n{'=' * 60}")
        print(f"  SUMMARY ({mode.upper()})")
        print("=" * 60)

        total_files = sum(r.files_processed for r in results)
        total_violations = sum(r.total_violations for r in results)
        total_fixed = sum(r.total_fixed for r in results)
        total_modified = sum(r.files_modified for r in results)
        total_rolled_back = sum(r.files_rolled_back for r in results)

        for r in results:
            if r.total_violations == 0:
                status = f"{Colors.GREEN}OK{Colors.NC}"
            else:
                status = f"{Colors.YELLOW}ISSUES{Colors.NC}"
            print(f"  {r.project:20} {status}")
            if r.total_violations > 0:
                print(f"    Violations: {r.total_violations}")
                if mode == "exec":
                    print(f"    Fixed: {r.total_fixed}")
                    print(f"    Files modified: {r.files_modified}")
                    if r.files_rolled_back > 0:
                        print(f"    Rolled back: {r.files_rolled_back}")

        print("-" * 60)
        print(f"  Total files processed: {total_files}")
        print(f"  Total violations: {total_violations}")
        if mode in {"dry-run", "exec"}:
            print(f"  Total fixes: {total_fixed}")
            print(f"  Files modified: {total_modified}")
            if total_rolled_back > 0:
                print(f"  Files rolled back: {total_rolled_back}")
        print("=" * 60)


class CLI:
    """Command-line interface."""

    def __init__(self) -> None:
        """Initialize CLI with processor."""
        self.processor = ProjectProcessor()
        self.summary_printer = SummaryPrinter()

    def run(self) -> int:
        """Main entry point."""
        parser = argparse.ArgumentParser(
            description="FLEXT Namespace Fix Script",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "mode",
            choices=["validate", "dry-run", "exec"],
            help="Operation mode",
        )
        parser.add_argument(
            "--project",
            "-p",
            choices=PROJECTS,
            help="Specific project to process (default: all)",
        )

        args = parser.parse_args()

        projects = [args.project] if args.project else PROJECTS
        mode: str = args.mode

        print(f"\n{'=' * 60}")
        print(f"  FLEXT Namespace Fix - {mode.upper()} Mode")
        print("=" * 60)

        results: list[ProjectResult] = []

        for project in projects:
            if mode == "validate":
                result = self.processor.validate_project(project)
            elif mode == "dry-run":
                result = self.processor.dry_run_project(project)
            else:  # exec
                result = self.processor.exec_project(project)
            results.append(result)

        self.summary_printer.print_summary(results, mode)

        # Return non-zero if there are violations
        total_violations = sum(r.total_violations for r in results)
        return 1 if total_violations > 0 and mode == "validate" else 0


def main() -> int:
    """Main function."""
    cli = CLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
