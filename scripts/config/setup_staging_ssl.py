#!/usr/bin/env python3
"""Setup SSL/TLS certificates for staging environment.

Enterprise SSL certificate management using flext_tools for maximum reliability.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from flext_tools import Colors, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata
from flext_tools.infrastructure import SSLManager


class StagingSSLSetup(FlextScript):
    """Setup SSL/TLS certificates for staging environment."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="setup_staging_ssl",
            description="Setup SSL/TLS certificates for staging environment",
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

        # Check OpenSSL availability
        try:
            import subprocess

            subprocess.run(
                ["openssl", "version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            print_colored("✅ OpenSSL available", Colors.GREEN)
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print_colored(
                "❌ OpenSSL not found - required for SSL certificate generation",
                Colors.RED,
            )
            return False

    def execute_main_logic(self, **kwargs: Any) -> bool:
        """Execute SSL setup logic."""
        try:
            project_root = Path.cwd()
            kwargs.get("force", False)

            print_colored("🔐 STAGING SSL SETUP", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.infrastructure for SSL operations
            ssl_manager = SSLManager()

            # Setup staging SSL configuration
            success = ssl_manager.setup_ssl(
                workspace_root=project_root,
                environment="staging",
            )

            if success:
                print_colored(
                    "✅ Staging SSL certificates configured successfully",
                    Colors.GREEN,
                )
                print_colored("🔗 Certificates available in ssl/staging/", Colors.CYAN)
                print_colored(
                    "📋 Configuration: ssl/staging/config/staging.conf",
                    Colors.CYAN,
                )
                return True
            print_colored("❌ Failed to setup SSL certificates", Colors.RED)
            return False

        except Exception as e:
            print_colored(f"❌ Error during SSL setup: {e}", Colors.RED)
            return False

    def create_parser(self) -> Any:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--force",
            action="store_true",
            help="Force regeneration of existing certificates",
        )

        return parser

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = StagingSSLSetup()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
