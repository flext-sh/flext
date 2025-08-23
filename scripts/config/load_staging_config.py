#!/usr/bin/env python3
"""Load and validate staging configuration."""

import argparse
import sys
from pathlib import Path

from flext_core import FlextResult

from flext_tools import Colors, FlextScript, ScriptMetadata, print_colored
from flext_tools.config import ConfigurationManager

# Apenas tipos internos de Python; argparse já importado acima


class StagingConfigLoader(FlextScript):
    """Load and validate staging configuration."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="load_staging_config",
            description="Load and validate staging environment configuration",
            category="config",
            version="2.0.0",
        )

    def validate_preconditions(self) -> FlextResult[None]:
        """Validate preconditions."""
        project_root = Path.cwd()

        # Check if we're in FLEXT workspace
        if not (project_root / "flext-api").exists():
            print_colored("❌ flext-api directory not found", Colors.RED)
            return FlextResult[None].fail("flext-api directory not found")

        # Check if staging config exists
        staging_env = project_root / "flext-api" / ".env.staging"
        if not staging_env.exists():
            print_colored("❌ .env.staging file not found in flext-api/", Colors.RED)
            return FlextResult[None].fail(".env.staging file not found in flext-api/")

        print_colored("✅ Staging configuration files found", Colors.GREEN)
        return FlextResult[None].ok(None)

    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
        """Execute staging config loading logic."""
        try:
            project_root = Path.cwd()
            validate_only = kwargs.get("validate_only", False)

            print_colored("⚙️ STAGING CONFIGURATION LOADER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.config for operations
            config_manager = ConfigurationManager()

            # Load and validate staging configuration
            success = config_manager.load_config(
                workspace_root=project_root,
                environment="staging",
            )

            if success:
                print_colored(
                    "✅ Staging configuration loaded successfully",
                    Colors.GREEN,
                )
                print_colored("📋 All environment variables validated", Colors.CYAN)
                return FlextResult[None].ok(
                    {"success": True, "validate_only": validate_only}
                )

            print_colored("❌ Failed to load staging configuration", Colors.RED)
            print_colored("Check .env.staging file for errors", Colors.YELLOW)
            return FlextResult[None].fail("Failed to load staging configuration")

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during config loading: {e}", Colors.RED)
            return FlextResult[None].fail(f"Config loading error: {e}")

    def create_parser(self) -> argparse.ArgumentParser:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--validate-only",
            action="store_true",
            help="Only validate configuration without loading",
        )

        return parser

    def cleanup(self) -> FlextResult[None]:
        """Limpeza após execução."""
        return FlextResult[None].ok(None)


def main() -> int:
    """Main function."""
    script = StagingConfigLoader()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
