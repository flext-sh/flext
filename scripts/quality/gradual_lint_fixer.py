#!/usr/bin/env python3
"""Gradual Lint Fixer.

Aplica correções seguras de linting graduais em projetos FLEXT
usando flext_tools.quality para máxima confiabilidade enterprise.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from flext_tools import Colors, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata
from flext_tools.quality import GradualLintFixer


class GradualLintFixerScript(FlextScript):
    """Apply gradual lint fixes to FLEXT projects safely."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="gradual_lint_fixer",
            description="Apply safe gradual lint fixes to projects",
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

        # Check Ruff availability
        try:
            subprocess.run(
                ["ruff", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            print_colored("✅ Ruff available", Colors.GREEN)
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print_colored(
                "❌ Ruff not found - install with: pip install ruff",
                Colors.RED,
            )
            return False

        # Check Git availability
        try:
            subprocess.run(
                ["git", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            print_colored("✅ Git available", Colors.GREEN)
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print_colored("❌ Git not found - required for safe branching", Colors.RED)
            return False

    def execute_main_logic(self, **kwargs: object) -> bool:
        """Execute gradual lint fixing."""
        try:
            workspace_root = Path.cwd()
            project = kwargs.get("project")
            safe_only = kwargs.get("safe_only", True)
            run_tests = kwargs.get("run_tests", True)

            if not project:
                print_colored("❌ Project name is required", Colors.RED)
                return False

            project_path = workspace_root / project
            if not project_path.exists():
                print_colored(f"❌ Project {project} not found", Colors.RED)
                return False

            print_colored("🔧 GRADUAL LINT FIXER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.quality for lint fixing
            lint_fixer = GradualLintFixer(workspace_path=workspace_root)

            # Apply gradual lint fixes
            fix_result = lint_fixer.fix_gradually(
                project_path=project_path,
                safe_only=safe_only,
                run_tests=run_tests,
            )

            if fix_result:
                print_colored("✅ Gradual lint fixes completed", Colors.GREEN)

                # Print summary
                fixes_applied = fix_result.get("fixed_issues", 0)
                if fixes_applied > 0:
                    print_colored(f"🔧 Applied {fixes_applied} lint fixes", Colors.CYAN)
                else:
                    print_colored(
                        "✨ No lint fixes needed - code is already clean!",
                        Colors.GREEN,
                    )

                return True
            print_colored("❌ Gradual lint fixing failed", Colors.RED)
            return False

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during lint fixing: {e}", Colors.RED)
            return False

    def create_parser(self) -> object:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "project",
            help="Target project name (e.g., flext-core, flext-api)",
        )

        parser.add_argument(
            "--unsafe",
            action="store_true",
            help="Allow potentially unsafe fixes (default: safe only)",
        )

        parser.add_argument(
            "--skip-tests",
            action="store_true",
            help="Skip running tests after applying fixes",
        )

        return parser

    def _process_kwargs(self, args: Any) -> dict[str, Any]:
        """Process arguments into kwargs."""
        kwargs: dict[str, Any] = {}
        kwargs["safe_only"] = not getattr(args, "unsafe", False)
        kwargs["run_tests"] = not getattr(args, "skip_tests", False)
        return kwargs

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = GradualLintFixerScript()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
