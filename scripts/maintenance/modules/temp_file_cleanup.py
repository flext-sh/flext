#!/usr/bin/env python3
"""Temporary File Cleanup Module

Automatically removes old temporary scripts and files from workspace.
Based on scripts/maintenance/cleanup_temp_scripts.py functionality.
"""

import re
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console

from .base import CustomFixModule, Issue


class TempFileCleanupModule(CustomFixModule):
    """Module for cleaning up temporary files and scripts."""

    name = "temp_file_cleanup"
    description = "Removes old temporary files and scripts from workspace"

    def __init__(self, max_age_days: int = 30, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_age_days = max_age_days
        self.console = Console()

    def find_temp_files(self, workspace_path: Path) -> list[Path]:
        """Find temporary files that exceed the maximum age."""
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
        old_files: list = []

        # Search patterns for temporary files
        temp_patterns = [
            "*/temp/**/*.py",
            "*/scripts/temp/**/*.py",
            "**/temp_*.py",
            "**/tmp_*.py",
            "**/*_temp.py",
            "**/*_tmp.py",
            "**/backup_*.py",
            "**/*.bak",
            "**/*.tmp",
            "**/.temp/**/*",
        ]

        # Search in common temp directories
        temp_dirs = [
            workspace_path / "scripts" / "temp",
            workspace_path / "temp",
            workspace_path / ".temp",
            *workspace_path.glob("*/scripts/temp"),
            *workspace_path.glob("*/temp"),
            *workspace_path.glob("*/.temp"),
        ]

        # Check specific temp directories
        for temp_dir in temp_dirs:
            if not temp_dir.exists():
                continue

            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age < cutoff_date:
                        old_files.append(file_path)

        # Check temp files by pattern across workspace
        for pattern in temp_patterns:
            for file_path in workspace_path.glob(pattern):
                if file_path.is_file():
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age < cutoff_date:
                        old_files.append(file_path)

        # Remove duplicates
        return list(set(old_files))

    def analyze_file_content(self, file_path: Path) -> dict[str, str]:
        """Analyze file content to extract metadata."""
        try:
            if file_path.suffix in {".py", ".md", ".txt", ".yml", ".yaml"}:
                content = file_path.read_text(encoding="utf-8")

                # Search for cleanup date patterns
                cleanup_pattern = r"CLEANUP SCHEDULED:\s*(\d{4}-\d{2}-\d{2})"
                cleanup_match = re.search(cleanup_pattern, content)

                # Search for purpose/objective
                purpose_patterns = [
                    r"Purpose:\s*(.+)",
                    r"Objective:\s*(.+)",
                    r"TODO:\s*(.+)",
                    r"FIXME:\s*(.+)",
                ]

                purpose = None
                for pattern in purpose_patterns:
                    match = re.search(pattern, content)
                    if match:
                        purpose = match.group(1).strip()
                        break

                return {
                    "cleanup_date": cleanup_match.group(1) if cleanup_match else None,
                    "purpose": purpose,
                    "is_temp_template": any(
                        marker in content
                        for marker in [
                            "TEMPORARY SCRIPT",
                            "TEMP FILE",
                            "DELETE AFTER",
                            "CLEANUP SCHEDULED",
                        ]
                    ),
                    "has_todo": "TODO" in content or "FIXME" in content,
                }
        except Exception:
            pass

        return {
            "cleanup_date": None,
            "purpose": None,
            "is_temp_template": False,
            "has_todo": False,
        }

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze workspace for temporary files that need cleanup."""
        issues: list = []

        # This module works at workspace level, not individual files
        # Check if this file itself is a temp file
        file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)

        # Check if file matches temp patterns
        is_temp_file = any(
            [
                "temp" in str(file_path).lower(),
                "tmp" in str(file_path).lower(),
                file_path.suffix in {".bak", ".tmp"},
                file_path.name.startswith(("temp_", "tmp_", "backup_")),
                file_path.name.endswith(("_temp.py", "_tmp.py", "_bak.py")),
            ]
        )

        if is_temp_file and file_age < cutoff_date:
            metadata = self.analyze_file_content(file_path)
            age_days = (datetime.now() - file_age).days

            issues.append(
                Issue(
                    line=1,
                    column=1,
                    code="TEMP001",
                    message=f"Temporary file older than {self.max_age_days} days (age: {
                        age_days
                    } days)",
                    suggestion=f"Consider removing this temporary file. Purpose: {
                        metadata.get('purpose', 'Unknown')
                    }",
                )
            )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply cleanup fixes (handled at workspace level)."""
        return content

    def cleanup_temp_files(self, workspace_path: Path = None) -> bool:
        """Remove old temporary files from workspace."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Cleaning temporary files in: {workspace_path}[/blue]"
            )
            self.console.print(
                f"[yellow]Maximum age: {self.max_age_days} days[/yellow]"
            )

        old_files = self.find_temp_files(workspace_path)

        if not old_files:
            if self.verbose:
                self.console.print("[green]No old temporary files found[/green]")
            return True

        if self.verbose:
            self.console.print(
                f"[yellow]Found {len(old_files)} old temporary files[/yellow]"
            )

        removed_count = 0
        for file_path in old_files:
            try:
                # Analyze content for more informative logs
                metadata = self.analyze_file_content(file_path)
                file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                age_days = (datetime.now() - file_age).days

                if self.verbose:
                    self.console.print(
                        f"[cyan]File: {file_path.relative_to(workspace_path)} (age: {
                            age_days
                        } days, purpose: {
                            metadata.get('purpose', 'Not specified')
                        })[/cyan]"
                    )

                if self.interactive:
                    confirm = self.console.input(f"Remove {file_path.name}? (y/N): ")
                    if confirm.lower() != "y":
                        continue

                if not self.dry_run:
                    file_path.unlink()
                    if self.verbose:
                        self.console.print(
                            f"[green]✅ Removed: {file_path.name}[/green]"
                        )
                    removed_count += 1
                    if self.verbose:
                        self.console.print(
                            f"[cyan][DRY RUN] Would remove: {file_path.name}[/cyan]"
                        )

            except Exception as e:
                if self.verbose:
                    self.console.print(
                        f"[red]❌ Error removing {file_path.name}: {e}[/red]"
                    )

        if self.verbose:
            action = "Would remove" if self.dry_run else "Removed"
            self.console.print(
                f"[bold green]{action} {len(old_files)} temporary files[/bold green]"
            )
            if not self.dry_run and removed_count > 0:
                self.console.print(
                    f"[green]Successfully removed {removed_count} files[/green]"
                )

        return True

    def run_workspace_cleanup(self, workspace_path: Path = None) -> bool:
        """Run temp file cleanup across the entire workspace."""
        return self.cleanup_temp_files(workspace_path)
