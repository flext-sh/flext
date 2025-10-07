#!/usr/bin/env python3
"""Oracle E2E Test Runner.

Orquestra testes E2E completos do ecossistema Oracle Database FLEXT
usando flext_tools.testing para máxima confiabilidade.
"""

import argparse
import sys
from pathlib import Path

from flext_core import FlextResult, FlextTypes
from flext_tests import FlextTestDocker

from flext_tools import Colors, FlextScript, ScriptMetadata, print_colored


class OracleE2ETestRunner(FlextScript):
    """Oracle E2E test runner using enterprise testing tools."""

    @property
    def metadata(self) -> ScriptMetadata:
        """Get script metadata."""
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
            return FlextResult[None].fail("Execute from FLEXT workspace root")

        print_colored("✅ FLEXT workspace detected", Colors.GREEN)

        # Check Docker availability via FlextTestDocker unified management
        try:
            docker_manager = FlextTestDocker()
            # FlextTestDocker automatically validates Docker connectivity during initialization
            print_colored("✅ Docker available via FlextTestDocker", Colors.GREEN)

            # Verify Docker daemon is responsive
            if docker_manager.client:
                print_colored("✅ Docker daemon responsive", Colors.GREEN)
            else:
                print_colored("❌ Docker daemon not responsive", Colors.RED)
                return FlextResult[None].fail("Docker daemon not responsive")

            return FlextResult[None].ok(None)
        except Exception as e:
            print_colored(
                f"❌ FlextTestDocker not available - required for Oracle E2E tests: {e}",
                Colors.RED,
            )
            return FlextResult[None].fail(
                f"FlextTestDocker not available - required for Oracle E2E tests: {e}",
            )

    def execute_main_logic(self, **kwargs: object) -> FlextResult[object]:
        """Execute Oracle E2E testing logic."""
        try:
            # Suppress unused kwargs warning
            _ = kwargs

            print_colored("🧪 ORACLE E2E TEST RUNNER", Colors.CYAN)
            print_colored("=" * 60, Colors.CYAN)

            # Oracle E2E test functionality to be implemented
            # Will use flext_tools.testing for E2E operations
            results = FlextResult[FlextTypes.Dict].fail(
                "E2E test execution not yet implemented"
            )

            if results.is_success:
                result_data = results.unwrap()
                if isinstance(result_data, dict) and result_data.get("success", False):
                    print_colored(
                        "✅ Oracle E2E tests completed successfully",
                        Colors.GREEN,
                    )
                    print_colored(
                        "📊 Test reports generated in .flext_logs/",
                        Colors.CYAN,
                    )
                return FlextResult[object].ok(None)
            print_colored("❌ Oracle E2E tests failed", Colors.RED)
            print_colored("📋 Check logs in .flext_logs/ for details", Colors.YELLOW)
            return FlextResult[object].fail("Oracle E2E tests failed")

        except (OSError, ValueError, TypeError) as e:
            print_colored(f"❌ Error during E2E testing: {e}", Colors.RED)
            return FlextResult[object].fail(f"Error during E2E testing: {e}")

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
        return FlextResult[None].ok(None)


def main() -> int:
    """Main function."""
    script = OracleE2ETestRunner()
    return script.main()


if __name__ == "__main__":
    sys.exit(main())
