#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-infra/SKILL.md
"""load_staging_config.py - Staging Configuration Loader Script.

This script loads and validates staging environment configuration for FLEXT projects.
It checks for the presence of required configuration files and validates environment variables.

Scope: CLI script for configuration management, ensuring staging environments are
properly set up before deployment or testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flext_core import FlextResult
from flext_quality.tools import (
    Colors,
    ConfigurationManager,
    FlextScriptService as FlextScript,
    ScriptMetadata,
    print_colored,
)


class StagingConfigLoader(FlextScript):
    """Load and validate staging configuration."""

    @property
    def metadata(self) -> ScriptMetadata:
        """Get script metadata."""
        return ScriptMetadata(
            name="load_staging_config",
            description="Load and validate staging environment configuration",
            category="config",
            version="2.0.0",
        )

    def validate_preconditions(self) -> FlextResult[bool]:
        """Validate preconditions."""
        project_root = Path.cwd()

        # Check if we're in FLEXT workspace
        if not (project_root / "flext-api").exists():
            print_colored("❌ flext-api directory not found", Colors.RED)
            return FlextResult[bool].fail("flext-api directory not found")

        # Check if staging config exists
        staging_env = project_root / "flext-api" / ".env.staging"
        if not staging_env.exists():
            print_colored("❌ .env.staging file not found in flext-api/", Colors.RED)
            return FlextResult[bool].fail(".env.staging file not found in flext-api/")

        print_colored("✅ Staging configuration files found", Colors.GREEN)
        return FlextResult[bool].ok(value=True)

    def execute_implementation(self, args: dict[str, object]) -> FlextResult[object]:
        """Execute the staging config loading logic."""
        try:
            validate_only = bool(args.get("validate_only"))

            print_colored("⚙️ STAGING CONFIGURATION LOADER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_quality.tools.config for operations
            config_manager = ConfigurationManager()

            # Load and validate staging configuration
            result = config_manager.load_config()
            success = result.is_success

            if success:
                print_colored(
                    "✅ Staging configuration loaded successfully",
                    Colors.GREEN,
                )
                print_colored("📋 All environment variables validated", Colors.CYAN)
                return FlextResult[t.GeneralValueType].ok(
                    {
                        "success": True,
                        "validate_only": validate_only,
                    },
                )

            print_colored("❌ Failed to load staging configuration", Colors.RED)
            print_colored("Check .env.staging file for errors", Colors.YELLOW)
            return FlextResult[t.GeneralValueType].fail("Failed to load staging configuration")

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during config loading: {e}", Colors.RED)
            return FlextResult[t.GeneralValueType].fail(f"Config loading error: {e}")

    def create_parser(self) -> argparse.ArgumentParser:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        _ = parser.add_argument(
            "--validate-only",
            action="store_true",
            help="Only validate configuration without loading",
        )

        return parser

    def cleanup(self) -> FlextResult[bool]:
        """Limpeza após execução."""
        return FlextResult[bool].ok(value=True)


def main() -> int:
    """Main function."""
    script = StagingConfigLoader()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
