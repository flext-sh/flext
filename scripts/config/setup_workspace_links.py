#!/usr/bin/env python3
"""Setup Workspace Links - Configuração de Links do Workspace.

Script para configurar links entre projetos do workspace FLEXT
usando flext_tools.poetry para desenvolvimento local.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from flext_tools import Colors, PoetryValidator, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata


class WorkspaceLinksSetup(FlextScript):
    """Setup development links between FLEXT workspace projects."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="setup_workspace_links",
            description="Configure Poetry development links between workspace projects",
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

        # Check Poetry availability
        try:
            import subprocess

            subprocess.run(
                ["poetry", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            print_colored("✅ Poetry available", Colors.GREEN)
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print_colored("❌ Poetry not found", Colors.RED)
            return False

    def execute_main_logic(self, **kwargs: Any) -> bool:
        """Execute workspace links setup."""
        try:
            workspace_root = Path.cwd()

            print_colored("🔗 WORKSPACE LINKS SETUP", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.poetry for operations
            poetry_ops = PoetryValidator()

            # Discover projects
            projects = self._discover_projects(workspace_root)

            total_linked = 0
            failed_projects: list[str] = []

            # Setup links for each project
            for project_path in projects:
                project_name = project_path.name

                print_colored(
                    f"\n📦 Setting up links for {project_name}...",
                    Colors.BLUE,
                )

                try:
                    # Use flext_tools for Poetry operations
                    success = poetry_ops.validate_project(project_path)

                    if success:
                        print_colored(
                            f"  ✅ {project_name}: Links configured",
                            Colors.GREEN,
                        )
                        total_linked += 1
                    else:
                        print_colored(
                            f"  ❌ {project_name}: Failed to setup links",
                            Colors.RED,
                        )
                        failed_projects.append(project_name)

                except Exception as e:
                    print_colored(f"  ❌ {project_name}: Error - {e}", Colors.RED)
                    failed_projects.append(project_name)

            # Summary
            self._print_summary(len(projects), total_linked, failed_projects)

            return len(failed_projects) == 0

        except Exception as e:
            print_colored(f"❌ Error during setup: {e}", Colors.RED)
            return False

    def _discover_projects(self, workspace_root: Path) -> list[Path]:
        """Discover FLEXT projects."""
        # Projects to ignore
        ignore_list = {"client-a-oud-mig", "client-b-meltano-native", "flexcore"}

        projects = [
            item
            for item in workspace_root.iterdir()
            if item.is_dir()
            and (item / "pyproject.toml").exists()
            and item.name not in ignore_list
            and not any(skip in item.name for skip in [".git", ".venv", "__pycache__"])
        ]

        return sorted(projects, key=lambda p: p.name)

    def _print_summary(
        self,
        total_projects: int,
        linked: int,
        failed_projects: list[str],
    ) -> None:
        """Print setup summary."""
        print_colored("\n📊 WORKSPACE LINKS SUMMARY", Colors.BLUE)
        print_colored("=" * 40, Colors.BLUE)

        print(f"  📁 Projects processed: {total_projects}")
        print(f"  ✅ Successfully linked: {linked}")
        print(f"  ❌ Failed: {len(failed_projects)}")

        if failed_projects:
            print_colored("\n🚫 Failed Projects:", Colors.RED)
            for project in failed_projects:
                print(f"  • {project}")

        # Success rate
        if total_projects > 0:
            success_rate = (linked / total_projects) * 100

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

            if success_rate == 100:
                print_colored(
                    "\n🎉 All workspace links configured successfully!",
                    Colors.GREEN,
                )
                print_colored(
                    "Projects can now use each other as development dependencies",
                    Colors.GREEN,
                )

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = WorkspaceLinksSetup()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
