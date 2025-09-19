#!/usr/bin/env python3
"""Gradual Lint Fixer.

Aplica correções seguras de linting graduais em projetos FLEXT
usando flext_tools.quality para máxima confiabilidade enterprise.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from flext_core import FlextResult, FlextTypes
from flext_tools import Colors, print_colored
from flext_tools.lint_fixer import GradualLintFixer
from flext_tools.script_base import FlextScript, ScriptMetadata


class GradualLintFixerScript(FlextScript):
    """Apply gradual lint fixes to FLEXT projects safely."""

    @property
    def metadata(self) -> ScriptMetadata:
        """Get script metadata."""
        return ScriptMetadata(
            name="gradual_lint_fixer",
            description="Apply safe gradual lint fixes to projects",
            category="quality",
            version="2.0.0",
        )

    def validate_preconditions(self) -> FlextResult[None]:
        """Validate preconditions."""
        workspace_root = Path.cwd()

        # Check if we're in FLEXT workspace
        if not (workspace_root / "pyproject.toml").exists():
            print_colored("❌ Execute from FLEXT workspace root", Colors.RED)
            return FlextResult[None].fail("Not in FLEXT workspace root")

        # Check Ruff availability
        if shutil.which("ruff") is None:
            print_colored(
                "❌ Ruff not found - install with: pip install ruff",
                Colors.RED,
            )
            return FlextResult[None].fail("Ruff not found")
        print_colored("✅ Ruff available", Colors.GREEN)

        # Check Git availability
        if shutil.which("git") is None:
            print_colored("❌ Git not found - required for safe branching", Colors.RED)
            return FlextResult[None].fail("Git not found")
        print_colored("✅ Git available", Colors.GREEN)
        return FlextResult[None].ok(None)

    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
        """Execute main script logic."""
        """Execute gradual lint fixing."""
        try:
            workspace_root = Path.cwd()
            project = kwargs.get("project")
            kwargs.get("safe_only", True)
            kwargs.get("run_tests", True)

            if not project:
                print_colored("❌ Project name is required", Colors.RED)
                return FlextResult[object].fail("Project name is required")

            project_path = workspace_root / str(project)
            if not project_path.exists():
                print_colored(f"❌ Project {project} not found", Colors.RED)
                return FlextResult[object].fail(f"Project {project} not found")

            print_colored("🔧 GRADUAL LINT FIXER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.quality for lint fixing
            lint_fixer = GradualLintFixer(workspace_path=workspace_root)

            # Apply gradual lint fixes
            fix_result = lint_fixer.fix_gradually()

            if fix_result:
                print_colored("✅ Gradual lint fixes completed", Colors.GREEN)

                # Print summary
                fixes_applied = fix_result.get("fixed_issues", 0)
                if isinstance(fixes_applied, (int, str)) and int(fixes_applied) > 0:
                    print_colored(f"🔧 Applied {fixes_applied} lint fixes", Colors.CYAN)
                else:
                    print_colored(
                        "✨ No lint fixes needed - code is already clean!",
                        Colors.GREEN,
                    )

                return FlextResult[object].ok(
                    {
                        "fix_result": fix_result,
                        "project": project,
                    },
                )

            print_colored("❌ Gradual lint fixing failed", Colors.RED)
            return FlextResult[object].fail("Gradual lint fixing failed")

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during lint fixing: {e}", Colors.RED)
            return FlextResult[object].fail(f"Error during lint fixing: {e}")

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

    def _process_kwargs(self, args: object) -> FlextTypes.Core.Dict:
        """Process arguments into kwargs."""
        kwargs: FlextTypes.Core.Dict = {}
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
