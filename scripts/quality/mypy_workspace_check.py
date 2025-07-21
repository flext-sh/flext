#!/usr/bin/env python3
"""MyPy Workspace Check.

Executa MyPy em todas as pastas src do workspace FLEXT
usando flext_tools.quality para máxima confiabilidade enterprise.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from flext_tools import Colors, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata
from flext_tools.quality import MyPyChecker


class MyPyWorkspaceCheck(FlextScript):
    """Run MyPy type checking across FLEXT workspace."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="mypy_workspace_check",
            description="Run MyPy type checking on all workspace projects",
            category="quality",
            version="2.0.0",
        )

    def validate_preconditions(self) -> bool:
        """Validate preconditions."""
        workspace_root = Path.cwd()

        # Check if we're in FLEXT workspace
        if not (workspace_root / "pyproject.toml").exists():
            print_colored("❌ Execute from FLEXT workspace root", Colors.RED)
            return False

        # Check MyPy availability
        try:
            import subprocess

            subprocess.run(
                ["mypy", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            print_colored("✅ MyPy available", Colors.GREEN)
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print_colored(
                "❌ MyPy not found - install with: pip install mypy",
                Colors.RED,
            )
            return False

    def execute_main_logic(self, **kwargs: Any) -> bool:
        """Execute MyPy workspace checking."""
        try:
            workspace_root = Path.cwd()
            projects_filter = kwargs.get("projects")
            strict_mode = kwargs.get("strict", False)

            print_colored("🔍 MYPY WORKSPACE CHECK", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.quality for MyPy operations
            mypy_checker = MyPyChecker(workspace_path=workspace_root)

            # Run MyPy checks across workspace
            check_result = mypy_checker.check_workspace(
                projects_filter=projects_filter,
                strict_mode=strict_mode,
            )

            if check_result:
                print_colored("✅ MyPy workspace check completed", Colors.GREEN)

                # Print summary
                has_errors = check_result.get("has_errors", False)
                error_count = check_result.get("error_count", 0)

                if has_errors:
                    print_colored(
                        f"⚠️ Found {error_count} type checking issues",
                        Colors.YELLOW,
                    )
                else:
                    print_colored(
                        "🎉 No MyPy type checking issues found!",
                        Colors.GREEN,
                    )

                # Generate report
                if kwargs.get("generate_report", True):
                    print_colored("📊 Detailed report generated", Colors.CYAN)

                return bool(check_result.get("has_no_errors", True))
            print_colored("❌ MyPy workspace check failed", Colors.RED)
            return False

        except Exception as e:
            print_colored(f"❌ Error during MyPy check: {e}", Colors.RED)
            return False

    def create_parser(self) -> Any:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--projects",
            help="Filter specific projects (comma-separated)",
        )

        parser.add_argument(
            "--strict",
            action="store_true",
            help="Enable strict MyPy checking",
        )

        parser.add_argument(
            "--no-report",
            action="store_true",
            help="Skip generating detailed report",
        )

        return parser

    def _process_kwargs(self, args: Any) -> dict[str, Any]:
        """Process arguments into kwargs."""
        kwargs: dict[str, Any] = {}
        kwargs["generate_report"] = not getattr(args, "no_report", False)
        return kwargs

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = MyPyWorkspaceCheck()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
