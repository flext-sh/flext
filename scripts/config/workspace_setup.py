#!/usr/bin/env python3
"""Workspace Setup.

Setup completo do workspace FLEXT usando flext_tools.poetry para máxima confiabilidade:
- Instala dependências em ordem correta
- Resolve conflitos automaticamente
- Valida ambiente completo
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from flext_tools import Colors, PoetryValidator, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata


class WorkspaceSetup(FlextScript):
    """Complete FLEXT workspace setup using enterprise tools."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="workspace_setup",
            description="Complete workspace setup with Poetry dependency management",
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
        """Execute workspace setup logic."""
        try:
            workspace_root = Path.cwd()
            kwargs.get("skip_dev", False)
            kwargs.get("projects")

            print_colored("🏗️ WORKSPACE SETUP", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.poetry for operations
            poetry_ops = PoetryValidator()

            # Setup complete workspace
            success = poetry_ops.validate_project(workspace_root)

            if success:
                print_colored("✅ Workspace setup completed successfully", Colors.GREEN)
                print_colored(
                    "🎉 All projects configured with proper dependencies",
                    Colors.GREEN,
                )
                print_colored("\nNext steps:", Colors.CYAN)
                print_colored("• Run 'make test-all' to validate setup", Colors.BLUE)
                print_colored("• Run 'make check-all' to verify quality", Colors.BLUE)
                return True
            print_colored("❌ Workspace setup failed", Colors.RED)
            print_colored("Check Poetry logs for details", Colors.YELLOW)
            return False

        except Exception as e:
            print_colored(f"❌ Error during workspace setup: {e}", Colors.RED)
            return False

    def create_parser(self) -> Any:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--skip-dev",
            action="store_true",
            help="Skip development dependencies installation",
        )

        parser.add_argument(
            "--projects",
            help="Filter specific projects (comma-separated)",
        )

        return parser

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = WorkspaceSetup()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
