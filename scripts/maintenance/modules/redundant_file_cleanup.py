#!/usr/bin/env python3
"""Redundant File Cleanup Module

Removes redundant and duplicate files after code unification.
Based on cleanup_redundant.py and cleanup_final.py functionality.
"""

import shutil
from pathlib import Path

from rich.console import Console

from .base import CustomFixModule, Issue


class RedundantFileCleanupModule(CustomFixModule):
    """Module for cleaning up redundant and duplicate files."""

    name = "redundant_file_cleanup"
    description = "Removes redundant and duplicate files after code unification"

    # Common redundant file patterns
    REDUNDANT_PATTERNS = [
        # Config redundancy patterns
        "**/modern_config.py",
        "**/advanced_config.py",
        "**/enterprise_config.py",
        "**/config_v*.py",
        "**/config_old.py",
        "**/config_backup.py",
        # Logging redundancy patterns
        "**/advanced_logging.py",
        "**/enterprise_logging.py",
        "**/unified_logging.py",
        "**/logging_v*.py",
        "**/logging_old.py",
        # CLI redundancy patterns
        "**/modern_cli.py",
        "**/recovery_cli.py",
        "**/cli_v*.py",
        "**/cli_old.py",
        "**/cli_backup.py",
        # Service redundancy patterns
        "**/advanced_*.py",
        "**/enterprise_*.py",
        "**/modern_*.py",
        "**/legacy_*.py",
        "**/old_*.py",
        "**/backup_*.py",
        # Monitoring redundancy patterns
        "**/modern_monitoring.py",
        "**/advanced_monitoring.py",
        "**/monitoring_v*.py",
        # Orchestrator redundancy patterns
        "**/modern_orchestrator.py",
        "**/advanced_orchestrator.py",
        "**/orchestrator_v*.py",
        # Database service redundancy
        "**/advanced_database_service.py",
        "**/enterprise_database_service.py",
        "**/database_service_v*.py",
        # Client redundancy
        "**/enterprise_*_client.py",
        "**/advanced_*_client.py",
        "**/client_v*.py",
        # General redundancy patterns
        "**/service_factory.py",  # Often replaced by unified services
        "**/*_factory.py",  # Factory patterns often consolidated
        "**/data_processor_*.py",  # Often redundant after unification
        "**/sync_engine_*.py",  # Often consolidated
        "**/validation_*.py",  # Often redundant with main validators
    ]

    # Cache and build artifact patterns
    CACHE_PATTERNS = [
        "**/__pycache__/**",
        "**/*.pyc",
        "**/*.pyo",
        "**/.mypy_cache/**",
        "**/.pytest_cache/**",
        "**/.coverage*",
        "**/htmlcov/**",
        "**/reports/**/*.html",
        "**/reports/**/*.xml",
        "**/.ruff_cache/**",
        "**/node_modules/**",
        "**/.venv/**",
        "**/venv/**",
        "**/env/**",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()

    def find_redundant_files(self, workspace_path: Path) -> dict[str, list[Path]]:
        """Find redundant files by patterns and similarity."""
        redundant_files = {
            "pattern_matches": [],
            "cache_files": [],
            "duplicate_content": [],
            "version_files": [],
        }

        # Find files matching redundant patterns
        for pattern in self.REDUNDANT_PATTERNS:
            for file_path in workspace_path.glob(pattern):
                if file_path.is_file():
                    redundant_files["pattern_matches"].append(file_path)

        # Find cache and build artifacts
        for pattern in self.CACHE_PATTERNS:
            for file_path in workspace_path.glob(pattern):
                if file_path.is_file():
                    redundant_files["cache_files"].append(file_path)

        # Find version-numbered files (likely duplicates)
        for py_file in workspace_path.rglob("*.py"):
            file_name = py_file.stem
            if any(
                suffix in file_name for suffix in ["_v1", "_v2", "_v3", "_v4", "_v5"]
            ):
                redundant_files["version_files"].append(py_file)

        # Find potential duplicate content files
        redundant_files["duplicate_content"] = self.find_duplicate_content_files(
            workspace_path
        )

        return redundant_files

    def find_duplicate_content_files(self, workspace_path: Path) -> list[Path]:
        """Find files with similar content that might be duplicates."""
        duplicate_files: list = []
        file_hashes: dict = {}

        for py_file in workspace_path.rglob("*.py"):
            if py_file.is_file():
                try:
                    content = py_file.read_text(encoding="utf-8")
                    # Simple content hash for duplicate detection
                    content_hash = hash(content.strip())

                    if content_hash in file_hashes:
                        # Found potential duplicate
                        original_file = file_hashes[content_hash]
                        # Keep the file with simpler name (usually the
                        # canonical one)
                        if len(py_file.name) > len(original_file.name):
                            duplicate_files.append(py_file)
                            duplicate_files.append(original_file)
                            file_hashes[content_hash] = py_file
                        file_hashes[content_hash] = py_file
                except Exception:
                    continue

        return duplicate_files

    def is_essential_file(self, file_path: Path) -> bool:
        """Check if a file is essential and should not be removed."""
        essential_patterns = [
            "__init__.py",
            "main.py",
            "cli.py",
            "config.py",
            "logging.py",
            "services.py",
            "pyproject.toml",
            "README.md",
            "requirements.txt",
            "Dockerfile",
            "Makefile",
            ".gitignore",
        ]

        # Check if file name matches essential patterns
        for pattern in essential_patterns:
            if file_path.name == pattern:
                return True

        # Check if file is in essential directories
        essential_dirs = ["src", "tests", "docs"]
        if any(part in essential_dirs for part in file_path.parts[-3:]):
            # More conservative - check if it's a main module file
            if file_path.suffix == ".py":
                # If it's the only file of its type in the directory, it's
                # probably essential
                parent_py_files = list(file_path.parent.glob(f"{file_path.stem}*.py"))
                if len(parent_py_files) == 1:
                    return True

        return False

    def analyze(self, file_path: Path, content: str) -> list[Issue]:
        """Analyze individual files for redundancy."""
        issues: list = []

        # Check if this file matches redundant patterns
        file_str = str(file_path)

        # Check against redundant patterns
        for pattern in self.REDUNDANT_PATTERNS:
            pattern_clean = pattern.replace("**/", "").replace("**", "")
            if pattern_clean in file_str or file_path.name.endswith(
                pattern_clean.replace("*.py", ".py")
            ):
                if not self.is_essential_file(file_path):
                    issues.append(
                        Issue(
                            line=1,
                            column=1,
                            code="REDUNDANT001",
                            message=f"File matches redundant pattern: {pattern_clean}",
                            suggestion="Consider removing this redundant file",
                        )
                    )

        # Check for version numbers in filename
        if any(
            suffix in file_path.stem
            for suffix in ["_v1", "_v2", "_v3", "_old", "_backup"]
        ):
            issues.append(
                Issue(
                    line=1,
                    column=1,
                    code="REDUNDANT002",
                    message="File appears to be a versioned or backup copy",
                    suggestion="Remove if superseded by newer version",
                )
            )

        # Check for redundant imports in content
        if file_path.suffix == ".py":
            lines = content.split("\n")
            redundant_import_patterns = [
                "from .modern_",
                "from .advanced_",
                "from .enterprise_",
                "from .old_",
                "from .legacy_",
            ]

            for i, line in enumerate(lines, 1):
                for pattern in redundant_import_patterns:
                    if pattern in line:
                        issues.append(
                            Issue(
                                line=i,
                                column=1,
                                code="REDUNDANT003",
                                message=f"Import from potentially redundant module: {pattern}",
                                suggestion="Update import to use unified module",
                            )
                        )

        return issues

    def apply_fixes(self, content: str, issues: list[Issue]) -> str:
        """Apply redundancy fixes to content."""
        lines = content.split("\n")

        for issue in issues:
            if issue.code == "REDUNDANT003":  # Fix redundant imports
                line_idx = issue.line - 1
                if line_idx < len(lines):
                    line = lines[line_idx]
                    # Replace redundant import patterns with standard ones
                    replacements = {
                        "from .modern_": "from .",
                        "from .advanced_": "from .",
                        "from .enterprise_": "from .",
                        "from .old_": "from .",
                        "from .legacy_": "from .",
                    }

                    for old_pattern, new_pattern in replacements.items():
                        if old_pattern in line:
                            lines[line_idx] = line.replace(old_pattern, new_pattern)
                            break

        return "\n".join(lines)

    def cleanup_redundant_files(self, workspace_path: Path = None) -> bool:
        """Remove redundant files from workspace."""
        if workspace_path is None:
            workspace_path = Path.cwd()

        if self.verbose:
            self.console.print(
                f"[blue]Cleaning redundant files in: {workspace_path}[/blue]"
            )

        redundant_files = self.find_redundant_files(workspace_path)

        total_files = sum(len(files) for files in redundant_files.values())

        if total_files == 0:
            if self.verbose:
                self.console.print("[green]No redundant files found[/green]")
            return True

        if self.verbose:
            self.console.print(f"[yellow]Found {total_files} redundant files:[/yellow]")
            for category, files in redundant_files.items():
                if files:
                    self.console.print(f"[cyan]  {category}: {len(files)} files[/cyan]")

        removed_count = 0

        for category, files in redundant_files.items():
            if self.verbose and files:
                self.console.print(f"\n[bold]Processing {category}:[/bold]")

            for file_path in files:
                try:
                    # Skip essential files
                    if self.is_essential_file(file_path):
                        if self.verbose:
                            self.console.print(
                                f"[yellow]⚠️  Skipping essential file: {
                                    file_path.name
                                }[/yellow]"
                            )
                        continue

                    if self.verbose:
                        rel_path = file_path.relative_to(workspace_path)
                        self.console.print(f"[cyan]  Checking: {rel_path}[/cyan]")

                    if self.interactive:
                        confirm = self.console.input(
                            f"Remove {file_path.name}? (y/N): "
                        )
                        if confirm.lower() != "y":
                            continue

                    if not self.dry_run:
                        if file_path.is_dir():
                            shutil.rmtree(file_path)
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
                f"\n[bold green]{action} {removed_count} redundant files[/bold green]"
            )

        return True

    def run_workspace_cleanup(self, workspace_path: Path = None) -> bool:
        """Run redundant file cleanup across the entire workspace."""
        return self.cleanup_redundant_files(workspace_path)
