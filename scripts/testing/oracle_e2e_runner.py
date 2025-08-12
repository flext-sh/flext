#!/usr/bin/env python3
"""Oracle E2E Test Runner.

Orquestra testes E2E completos do ecossistema Oracle Database FLEXT
usando flext_tools.testing para máxima confiabilidade.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from flext_core import FlextResult

from flext_tools import Colors, print_colored
from flext_tools.core.script_base import FlextScript, ScriptMetadata
from flext_tools.testing import OracleE2ETestManager

if TYPE_CHECKING:
    import argparse


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

    def validate_preconditions(self) -> FlextResult[None]:
        """Validate preconditions."""
        project_root = Path.cwd()

        # Check if we're in FLEXT workspace
        if not (project_root / "flext-core").exists():
            print_colored("❌ Execute from FLEXT workspace root", Colors.RED)
            return FlextResult.fail("Execute from FLEXT workspace root")

        print_colored("✅ FLEXT workspace detected", Colors.GREEN)

        # Check Docker availability
        try:
            docker_executable = shutil.which("docker")
            if not docker_executable:
                msg = "Docker executable not found."
                raise FileNotFoundError(msg)

            subprocess.run(  # noqa: S603
                [docker_executable, "--version"],  # Validated: uses docker from shutil.which
                capture_output=True,
                check=True,
                timeout=5,
                shell=False,  # Addressed S603
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
            return FlextResult.fail("Docker not found - required for Oracle E2E tests")

        # Check Docker Compose availability
        try:
            docker_executable = shutil.which(
                "docker"
            )  # Reusing docker_executable for 'docker compose'
            if not docker_executable:
                msg = "Docker executable not found for compose."
                raise FileNotFoundError(msg)

            subprocess.run(  # noqa: S603
                [docker_executable, "compose", "version"],  # Validated: uses docker from shutil.which
                capture_output=True,
                check=True,
                timeout=5,
                shell=False,  # Addressed S603
            )
            print_colored("✅ Docker Compose available", Colors.GREEN)
            return FlextResult.ok(None)
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
            print_colored("❌ Docker Compose not found", Colors.RED)
            return FlextResult.fail("Docker Compose not found")

    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
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
                return FlextResult.ok(None)
            print_colored("❌ Oracle E2E tests failed", Colors.RED)
            print_colored("📋 Check logs in .flext_logs/ for details", Colors.YELLOW)
            return FlextResult.fail("Oracle E2E tests failed")

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during E2E testing: {e}", Colors.RED)
            return FlextResult.fail(f"Error during E2E testing: {e}")

    def create_parser(self) -> argparse.ArgumentParser:
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

    def cleanup(self) -> FlextResult[None]:
        """Limpeza após execução."""
        return FlextResult.ok(None)


def main() -> int:
    """Main function."""
    script = OracleE2ETestRunner()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
