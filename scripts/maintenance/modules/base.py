"""
Base classes for custom fix modules.

Provides the foundation for all custom fix modules with dry-run
and confirmation capabilities.
"""

import difflib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.syntax import Syntax


class Severity(Enum):
    """Issue severity levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class FixResult:
    """Result of a fix operation."""

    success: bool
    file_path: Path
    issues_found: int
    issues_fixed: int
    error: Optional[str] = None
    diff: Optional[str] = None


@dataclass
class Issue:
    """Represents an issue found in code."""

    line: Optional[int]
    message: str
    severity: Severity
    file_path: Optional[Path] = None
    column: int = 0
    fix_description: str = ""
    original_line: str = ""
    fixed_line: str = ""


class CustomFixModule(ABC):
    """Base class for all custom fix modules."""

    def __init__(
        self, dry_run: bool = True, interactive: bool = False, verbose: bool = False
    ):
        """
        Initialize the fix module.

        Args:
            dry_run: If True, show changes without applying
            interactive: If True, ask for confirmation before fixes
            verbose: If True, show detailed output
        """
        self.dry_run = dry_run
        self.interactive = interactive
        self.verbose = verbose
        self.console = Console()

    @property
    @abstractmethod
    def name(self) -> str:
        """Module name."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Module description."""

    @property
    @abstractmethod
    def category(self) -> str:
        """Fix category (e.g., 'syntax', 'style', 'security')."""

    def process_file(self, file_path: Path) -> FixResult:
        """
        Process a single file.

        Args:
            file_path: Path to the file to process

        Returns:
            FixResult with operation details
        """
        try:
            # Read file content
            original_content = file_path.read_text(encoding="utf-8")

            # Analyze file for issues
            issues = self.analyze(file_path, original_content)

            if not issues:
                return FixResult(
                    success=True, file_path=file_path, issues_found=0, issues_fixed=0
                )

            # Show issues found
            if self.verbose:
                self._display_issues(file_path, issues)

            # Apply fixes
            if self.dry_run:
                # Generate diff without applying
                fixed_content = self.apply_fixes(original_content, issues)
                diff = self._generate_diff(original_content, fixed_content, file_path)

                return FixResult(
                    success=True,
                    file_path=file_path,
                    issues_found=len(issues),
                    issues_fixed=0,
                    diff=diff,
                )
            # Check for confirmation if in interactive mode
            if self.interactive:
                fixed_content = self.apply_fixes(original_content, issues)
                diff = self._generate_diff(original_content, fixed_content, file_path)

                self.console.print(
                    Panel(
                        Syntax(diff, "diff", theme="monokai"),
                        title=f"Changes for {file_path.name}",
                        border_style="yellow",
                    )
                )

                if not Confirm.ask("Apply these changes?"):
                    return FixResult(
                        success=True,
                        file_path=file_path,
                        issues_found=len(issues),
                        issues_fixed=0,
                    )

            # Apply fixes
            fixed_content = self.apply_fixes(original_content, issues)

            # Validate fixes
            if not self.validate_fixes(original_content, fixed_content):
                return FixResult(
                    success=False,
                    file_path=file_path,
                    issues_found=len(issues),
                    issues_fixed=0,
                    error="Fix validation failed",
                )

            # Write fixed content
            file_path.write_text(fixed_content, encoding="utf-8")

            return FixResult(
                success=True,
                file_path=file_path,
                issues_found=len(issues),
                issues_fixed=len(issues),
            )

        except Exception as e:
            return FixResult(
                success=False,
                file_path=file_path,
                issues_found=0,
                issues_fixed=0,
                error=str(e),
            )

    def process_directory(
        self, directory: Path, pattern: str = "*.py"
    ) -> list[FixResult]:
        """
        Process all matching files in a directory.

        Args:
            directory: Directory to process
            pattern: File pattern to match

        Returns:
            List of FixResult for each file
        """
        results: list[FixResult] = []

        # Find all matching files
        files = list(directory.rglob(pattern))

        if not files:
            self.console.print(
                f"No {pattern} files found in {directory}", style="yellow"
            )
            return results

        # Process each file
        with self.console.status(f"Processing {len(files)} files...") as status:
            for i, file_path in enumerate(files, 1):
                # Skip excluded paths
                if self._should_skip(file_path):
                    continue

                status.update(f"Processing [{i}/{len(files)}]: {file_path.name}")
                result = self.process_file(file_path)
                results.append(result)

                # Show progress
                if result.issues_found > 0:
                    if result.issues_fixed > 0:
                        self.console.print(
                            f"✅ Fixed {result.issues_fixed}/{result.issues_found} issues in {file_path.name}",
                            style="green",
                        )
                        self.console.print(
                            f"🔍 Found {result.issues_found} issues in {
                                file_path.name
                            }",
                            style="yellow",
                        )

        return results

    @abstractmethod
    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """
        Analyze file content and return list of issues.

        Args:
            file_path: Path to the file
            content: File content

        Returns:
            List of issues found
        """

    @abstractmethod
    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """
        Apply fixes to the content.

        Args:
            content: Original file content
            issues: List of issues to fix

        Returns:
            Fixed content
        """

    def validate_fixes(self, original: str, fixed: str) -> bool:
        """
        Validate that fixes are safe to apply.

        Args:
            original: Original content
            fixed: Fixed content

        Returns:
            True if fixes are valid
        """
        # Basic validation - can be overridden
        return len(fixed) > 0 and fixed != original

    def _display_issues(self, file_path: Path, issues: list[Issue]) -> None:
        """Display issues found in a file."""
        self.console.print(f"\n[bold]Issues in {file_path}:[/bold]")

        for issue in issues[:10]:  # Show first 10 issues
            severity_color = {
                Severity.HIGH: "red",
                Severity.MEDIUM: "yellow",
                Severity.LOW: "blue",
                Severity.INFO: "blue",
            }.get(issue.severity, "white")

            self.console.print(
                f"  Line {issue.line}: [{severity_color}]{issue.message}[/{
                    severity_color
                }]"
            )
            if issue.original_line:
                self.console.print(f"    - {issue.original_line.strip()}", style="dim")
            if issue.fixed_line:
                self.console.print(f"    + {issue.fixed_line.strip()}", style="green")

        if len(issues) > 10:
            self.console.print(f"  ... and {len(issues) - 10} more issues", style="dim")

    def _generate_diff(self, original: str, fixed: str, file_path: Path) -> str:
        """Generate a unified diff."""
        original_lines = original.splitlines(keepends=True)
        fixed_lines = fixed.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            n=3,
        )

        return "".join(diff)

    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            "__pycache__",
            ".venv",
            ".git",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
        ]

        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)

    def get_summary(self, results: list[FixResult]) -> dict[str, Any]:
        """Generate summary of results."""
        total_files = len(results)
        successful_files = sum(1 for r in results if r.success)
        total_issues = sum(r.issues_found for r in results)
        total_fixed = sum(r.issues_fixed for r in results)

        return {
            "module": self.name,
            "category": self.category,
            "total_files": total_files,
            "successful_files": successful_files,
            "failed_files": total_files - successful_files,
            "total_issues": total_issues,
            "total_fixed": total_fixed,
            "dry_run": self.dry_run,
            "errors": [r.error for r in results if r.error],
        }
