#!/usr/bin/env python3
"""
FLEXT Quality Issues Auto-Fix Tool
=================================

Automatically fixes common quality issues across all submodules:
- Syntax errors in Python code
- Common linting issues
- Missing __init__.py files
- Basic formatting issues

Author: FLEXT Automation


import re
import subprocess
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class QualityFixer:
    Fixes common quality issues automatically."""

    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root
        self.fixed_files: list[Path] = []
        self.errors_fixed = 0

    def fix_syntax_errors(self, file_path: Path) -> bool:
        Fix common syntax errors in Python files."""
        if file_path.suffix != ".py":
            return False

        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content

            # Fix hasattr syntax errors - common pattern in the codebase
            # Before: if hasattr(user, field)  # type: ignore[misc]  # type: ignore[misc]:
            # After: if hasattr(user, field):  # type: ignore[misc]
            content = re.sub(
                r"if hasattr\([^)]+\)\s+#[^:]*#[^:]*:",
                lambda m: m.group(0).split("#")[0].strip() + ":  # type: ignore[misc]",
                content,
            )

            # Fix line length issues by breaking long strings
            lines = content.split("\n")
            fixed_lines = []

            for line in lines:
                if len(line) > 88 and "description=" in line and '"' in line:
                    # Break long description strings
                    indent = len(line) - len(line.lstrip())
                    if 'description="' in line:
                        parts = line.split('description="')
                        if len(parts) == 2:
                            prefix = parts[0] + "description=("
                            desc_part = parts[1].rstrip('",')
                            # Break into multiple lines
                            if len(desc_part) > 50:
                                mid = len(desc_part) // 2
                                # Find good break point
                                break_point = desc_part.find(" ", mid)
                                if break_point > 0:
                                    line1 = (
                                        prefix + '"' + desc_part[:break_point] + ' "'
                                    )
                                    line2 = (
                                        " " * (indent + 4)
                                        + '"'
                                        + desc_part[break_point + 1 :]
                                        + '"'
                                    )
                                    line3 = " " * indent + "),"
                                    fixed_lines.extend([line1, line2, line3])
                                    continue

                fixed_lines.append(line)

            content = "\n".join(fixed_lines)

            # Remove commented-out code lines (ERA001)
            content = re.sub(
                r'^\s*#\s*"[^"]*",?\s*#.*$', "", content, flags=re.MULTILINE
            )

            # Fix missing docstrings for __init__ methods
            content = re.sub(
                r'(def __init__\([^)]*\) -> None:)\n(\s*)((?!"""|\'\'\')[^\n])',
                r'\1\n\2Initialize instance."""\n\2\3',
                content,
            )

            if content != original_content:
                # Backup original
                backup_path = file_path.with_suffix(file_path.suffix + ".backup")
                backup_path.write_text(original_content, encoding="utf-8")

                # Write fixed content
                file_path.write_text(content, encoding="utf-8")
                self.fixed_files.append(file_path)
                self.errors_fixed += 1
                return True

        except Exception as e:
            console.print(f"[red]❌ Error fixing {file_path}: {e}[/red]")
            return False

        return False

    def add_missing_init_files(self, project_path: Path) -> int:
        """Add missing __init__.py files to Python packages."""
        added = 0
        src_path = project_path / "src"

        if not src_path.exists():
            return added

        # Find directories that should be packages
        for py_file in src_path.rglob("*.py"):
            parent_dir = py_file.parent
            init_file = parent_dir / "__init__.py"

            if not init_file.exists() and parent_dir != src_path:
                # Create __init__.py
                init_file.write_text(
                    '"""Package initialization."""\n', encoding="utf-8"
                )
                console.print(f"[green]✓ Added {init_file}[/green]")
                added += 1

        return added

    def fix_project_quality(self, project_path: Path) -> dict[str, Any]:
        """Fix quality issues in a single project."""
        results = {
            "syntax_fixes": 0,
            "init_files_added": 0,
            "files_processed": 0,
        }

        if not project_path.is_dir():
            return results

        console.print(
            f"[cyan]🔧 Fixing quality issues in {project_path.name}...[/cyan]"
        )

        # Fix Python files
        for py_file in project_path.rglob("*.py"):
            if py_file.is_file():
                results["files_processed"] += 1
                if self.fix_syntax_errors(py_file):
                    results["syntax_fixes"] += 1

        # Add missing __init__.py files
        results["init_files_added"] = self.add_missing_init_files(project_path)

        return results

    def format_with_ruff(self, project_path: Path) -> bool:
        """Format code with ruff."""
        try:
            result = subprocess.run(
                ["ruff", "format", str(project_path)],
                check=False,
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
            )
            if result.returncode == 0:
                console.print(f"[green]✓ Formatted {project_path.name}[/green]")
                return True
            console.print(
                f"[yellow]⚠ Ruff format issues in {project_path.name}[/yellow]"
            )
            return False
        except Exception as e:
            console.print(f"[red]❌ Error formatting {project_path.name}: {e}[/red]")
            return False

    def run_quality_fixes(self) -> None:
        """Run quality fixes across all projects."""
        # Active projects
        active_projects = [
            "flext-core",
            "flext-auth",
            "flext-api",
            "flext-grpc",
            "flext-web",
            "flext-cli",
            "flext-plugin",
            "flext-observability",
            "flext-meltano",
            "flext-ldap",
            "flext-db-oracle",
            "flext-quality",
            "flext-tap-ldap",
            "flext-tap-oracle-oic",
            "flext-tap-oracle-wms",
            "flext-target-ldap",
            "flext-target-oracle",
            "flext-target-oracle-oic",
            "flext-dbt-ldap",
            "flext-oracle-oic-ext",
        ]

        console.print(
            Panel.fit(
                f"[bold cyan]🔧 FLEXT Quality Auto-Fix[/bold cyan]\n"
                f"Fixing quality issues in {len(active_projects)} projects"
            )
        )

        total_results = {
            "syntax_fixes": 0,
            "init_files_added": 0,
            "files_processed": 0,
            "projects_formatted": 0,
        }

        with Progress(:
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Fixing quality issues...", total=len(active_projects)
            )

            for project_name in active_projects:
                project_path = self.workspace_root / project_name

                if project_path.exists():
                    progress.update(task, description=f"Processing {project_name}...")

                    # Fix quality issues
                    results = self.fix_project_quality(project_path)

                    # Format with ruff
                    if self.format_with_ruff(project_path):
                        total_results["projects_formatted"] += 1

                    # Accumulate results
                    for key in results:
                        total_results[key] += results[key]

                progress.advance(task)

        # Show summary
        console.print(
            Panel.fit(
                f"[bold green]✅ Quality Fix Summary[/bold green]\n"
                f"Files processed: {total_results['files_processed']}\n"
                f"Syntax fixes: {total_results['syntax_fixes']}\n"
                f"__init__.py files added: {total_results['init_files_added']}\n"
                f"Projects formatted: {total_results['projects_formatted']}\n"
                f"Total files fixed: {len(self.fixed_files)}"
            )
        )

        if self.fixed_files:
            console.print("\n[yellow]📝 Fixed files (backups created):[/yellow]")
            for fixed_file in self.fixed_files[:10]:  # Show first 10
                console.print(f"  - {fixed_file}")
            if len(self.fixed_files) > 10:
                console.print(f"  ... and {len(self.fixed_files) - 10} more")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix FLEXT quality issues automatically"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="FLEXT workspace root directory",
    )

    args = parser.parse_args()

    if not args.workspace.exists():
        console.print(
            f"[red]❌ Workspace directory {args.workspace} does not exist[/red]"
        )
        return

    fixer = QualityFixer(args.workspace)
    fixer.run_quality_fixes()


if __name__ == "__main__":
    main()
