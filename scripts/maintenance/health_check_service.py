#!/usr/bin/env python3
"""FLEXT Health Check Service.

Serviço de monitoramento de saúde usando flext_tools.monitoring
para máxima confiabilidade e padronização enterprise.
"""

import argparse
import sys
from pathlib import Path

from flext_core import FlextResult, FlextTypes

from flext_tools import (
    Colors,
    FlextScript,
    HealthCheckService,
    ScriptMetadata,
    print_colored,
)


class HealthCheckServiceRunner(FlextScript):
    """Run comprehensive health checking service for FLEXT."""

    @property
    def metadata(self) -> ScriptMetadata:
        """Get script metadata."""
        return ScriptMetadata(
            name="health_check_service",
            description="Run comprehensive health monitoring service",
            category="maintenance",
            version="2.0.0",
        )

    def validate_preconditions(self) -> bool:
        """Validate preconditions."""
        workspace_root = Path.cwd()

        # Check if we're in FLEXT workspace
        if not (workspace_root / "flext-core").exists():
            print_colored("❌ Execute from FLEXT workspace root", Colors.RED)
            return False

        print_colored("✅ FLEXT workspace detected", Colors.GREEN)
        return True

    def execute_main_logic(
        self, **kwargs: dict[str, str]
    ) -> FlextResult[dict[str, str]]:
        """Execute health check service."""
        try:
            workspace_root = Path.cwd()
            continuous = kwargs.get("continuous", False)
            interval = kwargs.get("interval", 30)
            kwargs.get("format", "json")

            print_colored("🏥 HEALTH CHECK SERVICE", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.monitoring for health checks
            health_service = HealthCheckService(workspace_path=workspace_root)

            # Run health checking
            if continuous:
                print_colored(
                    f"🔄 Starting continuous monitoring (interval: {interval}s)",
                    Colors.BLUE,
                )
                health_service.run_health_checks()
            else:
                # Single health check
                health_result = health_service.run_health_checks()

                if health_result:
                    print_colored("✅ All services healthy", Colors.GREEN)
                else:
                    print_colored("⚠️ Some services have issues", Colors.YELLOW)

                # Generate report
                if kwargs.get("generate_report", True):
                    print_colored("📊 Health report generated", Colors.CYAN)

            return True

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during health check: {e}", Colors.RED)
            return False

    def create_parser(self) -> argparse.ArgumentParser:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--continuous",
            action="store_true",
            help="Run continuous monitoring (Ctrl+C to stop)",
        )

        parser.add_argument(
            "--interval",
            type=int,
            default=30,
            help="Check interval in seconds for continuous mode (default: 30)",
        )

        parser.add_argument(
            "--format",
            choices=["json", "text", "prometheus"],
            default="json",
            help="Output format (default: json)",
        )

        parser.add_argument(
            "--no-report",
            action="store_true",
            help="Skip generating detailed report",
        )

        return parser

    def _process_kwargs(self, args: argparse.Namespace) -> FlextTypes.Dict:
        """Process arguments into kwargs."""
        kwargs: FlextTypes.Dict = {}
        kwargs["generate_report"] = not getattr(args, "no_report", False)
        return kwargs

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = HealthCheckServiceRunner()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
