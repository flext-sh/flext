#!/usr/bin/env python3
"""Standardize pyproject.toml files across FLEXT workspace.

This script applies PEP 518/621 standards to all projects in the workspace
using flext_tools.poetry for professional enterprise standardization.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from flext_tools import Colors, PoetryValidator, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata


class PyprojectStandardizer(FlextScript):
    """Standardize pyproject.toml files across FLEXT workspace."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="standardize_pyproject",
            description="Apply PEP 518/621 standards to all pyproject.toml files",
            category="config",
            version="2.0.0",
        )

    def validate_preconditions(self) -> bool:
        """Validate preconditions."""
        workspace_root = Path.cwd()

        # Check if we're in FLEXT workspace
        flext_projects = [
            p
            for p in workspace_root.iterdir()
            if p.is_dir()
            and p.name.startswith("flext-")
            and (p / "pyproject.toml").exists()
        ]

        if not flext_projects:
            print_colored("❌ Execute from FLEXT workspace root", Colors.RED)
            return False

        print_colored(f"✅ Found {len(flext_projects)} FLEXT projects", Colors.GREEN)
        return True

    def execute_main_logic(self, **kwargs: Any) -> bool:
        """Execute pyproject.toml standardization."""
        try:
            workspace_root = Path.cwd()
            projects_filter = kwargs.get("projects")

            print_colored("🔧 PYPROJECT.TOML STANDARDIZATION", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Discover projects
            projects = self._discover_projects(workspace_root, projects_filter)

            # Use flext_tools.poetry for operations
            poetry_ops = PoetryValidator()

            total_standardized = 0
            failed_projects: list[str] = []

            # Standardize each project
            for project_path in projects:
                project_name = project_path.name

                print_colored(f"\n📦 Standardizing {project_name}...", Colors.BLUE)

                try:
                    # Use flext_tools for standardization
                    success = poetry_ops.validate_project(project_path)

                    if success:
                        print_colored(
                            f"  ✅ {project_name}: Standardized",
                            Colors.GREEN,
                        )
                        total_standardized += 1
                    else:
                        print_colored(
                            f"  ❌ {project_name}: Failed to standardize",
                            Colors.RED,
                        )
                        failed_projects.append(project_name)

                except Exception as e:
                    print_colored(f"  ❌ {project_name}: Error - {e}", Colors.RED)
                    failed_projects.append(project_name)

            # Summary
            self._print_summary(len(projects), total_standardized, failed_projects)

            return len(failed_projects) == 0

        except Exception as e:
            print_colored(f"❌ Error during standardization: {e}", Colors.RED)
            return False

    def _discover_projects(
        self,
        workspace_root: Path,
        projects_filter: str | None = None,
    ) -> list[Path]:
        """Discover projects to standardize."""
        from scripts.common import discover_projects
        return discover_projects(workspace_root, projects_filter)

    def _print_summary(
        self,
        total_projects: int,
        standardized: int,
        failed_projects: list[str],
    ) -> None:
        """Print standardization summary."""
        print_colored("\n📊 STANDARDIZATION SUMMARY", Colors.BLUE)
        print_colored("=" * 40, Colors.BLUE)

        print(f"  📁 Projects processed: {total_projects}")
        print(f"  ✅ Successfully standardized: {standardized}")
        print(f"  ❌ Failed: {len(failed_projects)}")

        if failed_projects:
            print_colored("\n🚫 Failed Projects:", Colors.RED)
            for project in failed_projects:
                print(f"  • {project}")

        # Success rate
        if total_projects > 0:
            success_rate = (standardized / total_projects) * 100

            if success_rate == 100:
                status_color = Colors.GREEN
                status = "PERFECT"
            elif success_rate >= 90:
                status_color = Colors.CYAN
                status = "EXCELLENT"
            elif success_rate >= 80:
                status_color = Colors.YELLOW
                status = "GOOD"
            else:
                status_color = Colors.RED
                status = "NEEDS ATTENTION"

            print_colored(
                f"\n🏆 Success Rate: {success_rate:.1f}% ({status})",
                status_color,
            )

    def create_parser(self) -> Any:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--projects",
            help="Filter specific projects (comma-separated)",
        )

        return parser

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = PyprojectStandardizer()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
