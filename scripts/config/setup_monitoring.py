#!/usr/bin/env python3
"""Setup real monitoring infrastructure for FLEXT.

Setup completo de infraestrutura de monitoramento usando flext_tools.infrastructure
para máxima confiabilidade e padronização enterprise.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from flext_tools import Colors, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata
from flext_tools.infrastructure import MonitoringManager


class MonitoringSetup(FlextScript):
    """Setup monitoring infrastructure for FLEXT workspace."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="setup_monitoring",
            description="Setup Prometheus, Grafana and alerting infrastructure",
            category="config",
            version="2.0.0",
        )

    def validate_preconditions(self) -> bool:
        """Validate preconditions."""
        project_root = Path.cwd()

        # Check if we're in FLEXT workspace
        if not (project_root / "flext-core").exists():
            print_colored("❌ Execute from FLEXT workspace root", Colors.RED)
            return False

        print_colored("✅ FLEXT workspace detected", Colors.GREEN)

        # Check Docker availability for monitoring containers
        try:
            import subprocess

            subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            print_colored("✅ Docker available for monitoring containers", Colors.GREEN)
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print_colored(
                "❌ Docker not found - required for monitoring infrastructure",
                Colors.RED,
            )
            return False

    def execute_main_logic(self, **kwargs: Any) -> bool:
        """Execute monitoring setup logic."""
        try:
            project_root = Path.cwd()
            environment = kwargs.get("environment", "staging")
            kwargs.get("skip_containers", False)

            print_colored("📊 MONITORING INFRASTRUCTURE SETUP", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.infrastructure for monitoring operations
            monitoring_manager = MonitoringManager()

            # Setup complete monitoring stack
            success = monitoring_manager.setup_monitoring(
                workspace_root=project_root,
                environment=environment,
            )

            if success:
                print_colored(
                    "✅ Monitoring infrastructure configured successfully",
                    Colors.GREEN,
                )
                print_colored(
                    "📊 Prometheus, Grafana and alerts configured",
                    Colors.CYAN,
                )
                print_colored("🔗 Access Grafana at http://localhost:3000", Colors.BLUE)
                print_colored("📈 Prometheus at http://localhost:9090", Colors.BLUE)
                return True
            print_colored("❌ Failed to setup monitoring infrastructure", Colors.RED)
            return False

        except Exception as e:
            print_colored(f"❌ Error during monitoring setup: {e}", Colors.RED)
            return False

    def create_parser(self) -> Any:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--environment",
            default="staging",
            choices=["staging", "production", "development"],
            help="Target environment for monitoring setup",
        )

        parser.add_argument(
            "--skip-containers",
            action="store_true",
            help="Skip Docker container setup (config files only)",
        )

        return parser

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = MonitoringSetup()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
