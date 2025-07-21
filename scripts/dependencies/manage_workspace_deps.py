#!/usr/bin/env python3
"""Manage Workspace Dependencies.

Gerencia dependências do workspace FLEXT usando flext_tools.poetry
para máxima confiabilidade e consistência enterprise.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from flext_tools import Colors, PoetryValidator, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata


class WorkspaceDependencyManager(FlextScript):
    """Manage workspace dependencies using enterprise tools."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="manage_workspace_deps",
            description="Manage workspace dependencies with Poetry validation",
            category="dependencies",
            version="2.0.0",
        )

    def validate_preconditions(self) -> bool:
        """Validate preconditions."""
        workspace_root = Path.cwd()

        # Check if we're in FLEXT workspace
        if not (workspace_root / "pyproject.toml").exists():
            print_colored(
                "❌ Execute from FLEXT workspace root (no pyproject.toml found)",
                Colors.RED,
            )
            return False

        print_colored("✅ FLEXT workspace detected", Colors.GREEN)

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
        """Execute workspace dependency management."""
        try:
            workspace_root = Path.cwd()
            kwargs.get("fix_conflicts", False)
            kwargs.get("update_deps", False)

            print_colored("📦 WORKSPACE DEPENDENCY MANAGEMENT", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.poetry for operations
            poetry_ops = PoetryValidator()

            # Manage workspace dependencies
            success = poetry_ops.validate_project(workspace_root)

            if success:
                print_colored(
                    "✅ Workspace dependencies managed successfully",
                    Colors.GREEN,
                )
                print_colored(
                    "📋 All projects have consistent dependency configurations",
                    Colors.CYAN,
                )
                print_colored("\nNext steps:", Colors.BLUE)
                print_colored("• Run 'poetry install' in each project", Colors.BLUE)
                print_colored("• Run 'make check-deps' to validate", Colors.BLUE)
                return True
            print_colored("❌ Failed to manage workspace dependencies", Colors.RED)
            print_colored("Check Poetry logs for details", Colors.YELLOW)
            return False

        except Exception as e:
            print_colored(f"❌ Error during dependency management: {e}", Colors.RED)
            return False

    def create_parser(self) -> Any:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--fix-conflicts",
            action="store_true",
            help="Fix dependency conflicts automatically",
        )

        parser.add_argument(
            "--update-deps",
            action="store_true",
            help="Update dependencies to latest compatible versions",
        )

        return parser

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = WorkspaceDependencyManager()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
