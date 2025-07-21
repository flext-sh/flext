#!/usr/bin/env python3
"""Oracle E2E Test Runner.

Orquestra testes E2E completos do ecossistema Oracle Database FLEXT
usando flext_tools.testing para máxima confiabilidade.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from flext_tools import Colors, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata
from flext_tools.testing import OracleE2ETestManager


class OracleE2ETestRunner(FlextScript):
    """Oracle E2E test runner using enterprise testing tools."""

    @property
    def metadata(self) -> ScriptMetadata:
        return ScriptMetadata(
            name="oracle_e2e_runner",
            description="Run complete Oracle E2E test suite",
            category="testing",
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

        # Check Docker availability
        try:
            import subprocess

            subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            print_colored("✅ Docker available", Colors.GREEN)
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print_colored(
                "❌ Docker not found - required for Oracle E2E tests",
                Colors.RED,
            )
            return False

        # Check Docker Compose availability
        try:
            subprocess.run(
                ["docker", "compose", "version"],
                capture_output=True,
                check=True,
                timeout=5,
            )
            print_colored("✅ Docker Compose available", Colors.GREEN)
            return True
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print_colored("❌ Docker Compose not found", Colors.RED)
            return False

    def execute_main_logic(self, **kwargs: Any) -> bool:
        """Execute Oracle E2E testing logic."""
        try:
            project_root = Path.cwd()
            test_filter = kwargs.get("test_filter")
            skip_build = kwargs.get("skip_build", False)
            timeout = kwargs.get("timeout", 1800)  # 30 minutes default

            print_colored("🧪 ORACLE E2E TEST RUNNER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Use flext_tools.testing for E2E operations
            test_manager = OracleE2ETestManager(workspace_path=project_root)

            # Run Oracle E2E test suite
            results = test_manager.run_e2e_tests(
                test_filter=test_filter,
                skip_build=skip_build,
                timeout=timeout,
            )

            if results.get("success", False):
                print_colored(
                    "✅ Oracle E2E tests completed successfully",
                    Colors.GREEN,
                )
                print_colored("📊 Test reports generated in .flext_logs/", Colors.CYAN)
                return True
            print_colored("❌ Oracle E2E tests failed", Colors.RED)
            print_colored("📋 Check logs in .flext_logs/ for details", Colors.YELLOW)
            return False

        except Exception as e:
            print_colored(f"❌ Error during E2E testing: {e}", Colors.RED)
            return False

    def create_parser(self) -> Any:
        """Create parser with specific arguments."""
        parser = super().create_parser()

        parser.add_argument(
            "--test-filter",
            help="Filter specific tests (comma-separated)",
        )

        parser.add_argument(
            "--skip-build",
            action="store_true",
            help="Skip Docker image builds",
        )

        parser.add_argument(
            "--timeout",
            type=int,
            default=1800,
            help="Test timeout in seconds (default: 1800)",
        )

        return parser

    def cleanup(self) -> None:
        """Limpeza após execução."""


def main() -> int:
    """Main function."""
    script = OracleE2ETestRunner()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
