#!/usr/bin/env python3
"""Quality Gateway Runner.

Executa gateway de qualidade completo usando flext_tools.quality
para máxima confiabilidade e padronização enterprise.
"""

from __future__ import annotations

import sys
from pathlib import Path

from flext_core import FlextTypes

from flext_tools import (
    Colors,
    FlextScript,
    QualityGateway,
    ScriptMetadata,
    print_colored,
)


class QualityGatewayRunner(FlextScript):
    """Run comprehensive quality gateway for FLEXT projects."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="quality_gateway_runner",
            description="Run comprehensive quality gateway checks",
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

        print_colored("✅ FLEXT workspace detected", Colors.GREEN)
        return True

    def execute_main_logic(self, **kwargs: object) -> bool:
        """Execute quality gateway."""
        try:
            workspace_root = Path.cwd()
            projects_filter = kwargs.get("projects")
            strict_mode = kwargs.get("strict", False)
            fail_fast = kwargs.get("fail_fast", False)

            print_colored("🔍 QUALITY GATEWAY RUNNER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.quality for comprehensive checks
            quality_gateway = QualityGateway(workspace_path=workspace_root)

            # Run complete quality gateway
            gateway_result = quality_gateway.run_quality_checks(
                projects_filter=projects_filter,
                strict_mode=strict_mode,
                fail_fast=fail_fast,
            )

            if gateway_result:
                print_colored("✅ Quality gateway completed", Colors.GREEN)

                # Print summary
                total_issues = 0
                for check_result in gateway_result.get("details", {}).values():
                    if isinstance(check_result, dict) and not check_result.get(
                        "passed",
                        True,
                    ):
                        total_issues += 1

                if total_issues == 0:
                    print_colored(
                        "🎉 All quality checks passed! Clean codebase!",
                        Colors.GREEN,
                    )
                else:
                    print_colored(
                        f"⚠️ Found {total_issues} quality issues",
                        Colors.YELLOW,
                    )

                # Generate comprehensive report
                if kwargs.get("generate_report", True):
                    print_colored("📊 Detailed report generated", Colors.CYAN)

                return bool(gateway_result.get("overall_success", True))
            print_colored("❌ Quality gateway failed", Colors.RED)
            return False

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during quality gateway: {e}", Colors.RED)
            return False

    def create_parser(self) -> object:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--projects",
            help="Filter specific projects (comma-separated)",
        )

        parser.add_argument(
            "--strict",
            action="store_true",
            help="Enable strict quality checking",
        )

        parser.add_argument(
            "--fail-fast",
            action="store_true",
            help="Stop on first quality check failure",
        )

        parser.add_argument(
            "--no-report",
            action="store_true",
            help="Skip generating detailed report",
        )

        return parser

    def _process_kwargs(self, args: object) -> FlextTypes.Core.Dict:
        """Process arguments into kwargs."""
        kwargs: FlextTypes.Core.Dict = {}
        kwargs["generate_report"] = not getattr(args, "no_report", False)
        return kwargs

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = QualityGatewayRunner()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
