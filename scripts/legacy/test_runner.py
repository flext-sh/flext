#!/usr/bin/env python3
"""Modern test runner for client-a OUD Migration with comprehensive quality checks.

This script provides a comprehensive testing suite with:
- Lint checks with ruff (strict mode)
- Type checking with mypy (strict mode)
- Security analysis with bandit
- Test execution with pytest and coverage
- Integration tests with .env support
- Performance and memory profiling
- Report generation (HTML, XML, JSON)

Usage:
    python scripts/test_runner.py [options]

Environment:
    Uses /home/marlonsc/flext/.venv/bin/python for all operations
    Conditionally uses .env for integration/e2e tests if present
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
VENV_PYTHON = Path("/home/marlonsc/flext/.venv/bin/python")
VENV_BIN = VENV_PYTHON.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Tool paths
PYTEST = VENV_BIN / "pytest"
RUFF = VENV_BIN / "ruff"
MYPY = VENV_BIN / "mypy"
BANDIT = VENV_BIN / "bandit"
COVERAGE = VENV_BIN / "coverage"

# Report directories
REPORTS_DIR = PROJECT_ROOT / "reports"
COVERAGE_DIR = REPORTS_DIR / "coverage"


class TestResult:
    """Test result container."""

    def __init__(
        self, name: str, success: bool, duration: float, details: str = "",
    ) -> None:
        self.name = name
        self.success = success
        self.duration = duration
        self.details = details
        self.timestamp = datetime.now()


class ModernTestRunner:
    """Modern test runner with comprehensive quality checks."""

    def __init__(self, verbose: bool = True, strict: bool = True) -> None:
        self.verbose = verbose
        self.strict = strict
        self.results: list[TestResult] = []
        self.env_available = ENV_FILE.exists()

        # Ensure report directories exist
        REPORTS_DIR.mkdir(exist_ok=True)
        COVERAGE_DIR.mkdir(exist_ok=True)

        if self.verbose:
            print("🚀 Modern Test Runner for client-a OUD Migration")
            print(f"📁 Project: {PROJECT_ROOT}")
            print(f"🐍 Python: {VENV_PYTHON}")
            print(f"📄 .env available: {self.env_available}")
            print(f"🔒 Strict mode: {self.strict}")
            print()

    def run_command(
        self,
        cmd: list[str],
        name: str,
        env: dict[str, str] | None = None,
        capture_output: bool = True,
    ) -> TestResult:
        """Run a command and return result."""
        if self.verbose:
            print(f"🔄 Running {name}...")

        start_time = time.time()

        try:
            # Merge environment
            run_env = os.environ.copy()
            if env:
                run_env.update(env)

            result = subprocess.run(
                cmd,
                check=False, cwd=PROJECT_ROOT,
                env=run_env,
                capture_output=capture_output,
                text=True,
                timeout=300,  # 5 minutes timeout
            )

            duration = time.time() - start_time
            success = result.returncode == 0

            if capture_output:
                details = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            else:
                details = f"Exit code: {result.returncode}"

            if self.verbose:
                status = "✅" if success else "❌"
                print(f"{status} {name} ({duration:.2f}s)")
                if not success and capture_output:
                    print(f"   Error: {result.stderr.strip()}")

            return TestResult(name, success, duration, details)

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            if self.verbose:
                print(f"⏰ {name} timed out ({duration:.2f}s)")
            return TestResult(name, False, duration, "Command timed out")

        except Exception as e:
            duration = time.time() - start_time
            if self.verbose:
                print(f"💥 {name} failed with exception: {e}")
            return TestResult(name, False, duration, f"Exception: {e}")

    def run_linting(self) -> TestResult:
        """Run ruff linting with strict configuration."""
        cmd = [
            str(RUFF),
            "check",
            "--select",
            "ALL",
            "--config",
            str(PROJECT_ROOT / "pyproject.toml"),
            "src/",
            "tests/",
        ]
        return self.run_command(cmd, "Ruff Linting (Strict)")

    def run_formatting_check(self) -> TestResult:
        """Check code formatting with ruff."""
        cmd = [
            str(RUFF),
            "format",
            "--check",
            "--config",
            str(PROJECT_ROOT / "pyproject.toml"),
            "src/",
            "tests/",
        ]
        return self.run_command(cmd, "Ruff Formatting Check")

    def run_type_checking(self) -> TestResult:
        """Run mypy type checking in strict mode."""
        cmd = [
            str(MYPY),
            "--config-file",
            str(PROJECT_ROOT / "pyproject.toml"),
            "--strict",
            "src/",
        ]
        return self.run_command(cmd, "MyPy Type Checking (Strict)")

    def run_security_analysis(self) -> TestResult:
        """Run security analysis with bandit."""
        cmd = [
            str(BANDIT),
            "-r",
            "src/",
            "-f",
            "json",
            "-o",
            str(REPORTS_DIR / "bandit_report.json"),
        ]
        return self.run_command(cmd, "Bandit Security Analysis")

    def run_unit_tests(self) -> TestResult:
        """Run unit tests with coverage."""
        cmd = [
            str(PYTEST),
            "tests/unit/",
            "-v",
            "--strict-markers",
            "--strict-config",
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html:" + str(COVERAGE_DIR),
            "--cov-report=xml:" + str(REPORTS_DIR / "coverage.xml"),
            "--junitxml=" + str(REPORTS_DIR / "pytest_unit.xml"),
            "--tb=short",
            "--maxfail=5",
        ]
        return self.run_command(cmd, "Unit Tests + Coverage", capture_output=False)

    def run_integration_tests(self) -> TestResult:
        """Run integration tests (with .env if available)."""
        env = {}
        if self.env_available:
            # Load .env file for integration tests
            with open(ENV_FILE, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env[key.strip()] = value.strip()

        cmd = [
            str(PYTEST),
            "tests/integration/",
            "-v",
            "--strict-markers",
            "--strict-config",
            "--junitxml=" + str(REPORTS_DIR / "pytest_integration.xml"),
            "--tb=short",
            "--maxfail=3",
        ]

        if self.env_available:
            cmd.extend(["--env-file", str(ENV_FILE)])

        return self.run_command(cmd, "Integration Tests", env=env, capture_output=False)

    def run_e2e_tests(self) -> TestResult:
        """Run end-to-end tests (conditional on .env)."""
        if not self.env_available:
            return TestResult("E2E Tests", True, 0.0, "Skipped - no .env file")

        # Load environment for E2E tests
        env = {}
        with open(ENV_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()

        cmd = [
            str(PYTEST),
            "tests/e2e/",
            "-v",
            "--strict-markers",
            "--strict-config",
            "--junitxml=" + str(REPORTS_DIR / "pytest_e2e.xml"),
            "--tb=short",
            "--maxfail=1",
        ]

        return self.run_command(cmd, "E2E Tests", env=env, capture_output=False)

    def run_performance_tests(self) -> TestResult:
        """Run performance tests with benchmarking."""
        cmd = [
            str(PYTEST),
            "tests/",
            "-v",
            "-m",
            "performance",
            "--benchmark-only",
            "--benchmark-json=" + str(REPORTS_DIR / "benchmark.json"),
            "--junitxml=" + str(REPORTS_DIR / "pytest_performance.xml"),
        ]
        return self.run_command(cmd, "Performance Tests", capture_output=False)

    def generate_coverage_report(self) -> TestResult:
        """Generate comprehensive coverage report."""
        # Generate coverage badge data
        cmd = [
            str(COVERAGE),
            "json",
            "--data-file=" + str(REPORTS_DIR / ".coverage"),
            "-o",
            str(REPORTS_DIR / "coverage_summary.json"),
        ]
        return self.run_command(cmd, "Coverage Report Generation")

    def lint_test_files(self) -> TestResult:
        """Ensure test files themselves pass linting."""
        cmd = [
            str(RUFF),
            "check",
            "--select",
            "ALL",
            "--config",
            str(PROJECT_ROOT / "pyproject.toml"),
            "tests/",
        ]
        return self.run_command(cmd, "Test Files Linting")

    def type_check_test_files(self) -> TestResult:
        """Type check test files."""
        cmd = [
            str(MYPY),
            "--config-file",
            str(PROJECT_ROOT / "pyproject.toml"),
            "tests/",
        ]
        return self.run_command(cmd, "Test Files Type Checking")

    def generate_final_report(self) -> None:
        """Generate final comprehensive test report."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        total_duration = sum(r.duration for r in self.results)

        # Calculate coverage if available
        coverage_data = {}
        coverage_file = REPORTS_DIR / "coverage_summary.json"
        if coverage_file.exists():
            try:
                with open(coverage_file, encoding="utf-8") as f:
                    coverage_data = json.load(f)
            except Exception as e:
                pass

        report = {
            "timestamp": datetime.now().isoformat(),
            "project": "client-a-oud-mig",
            "python_version": subprocess.run(
                [str(VENV_PYTHON), "--version"],
                check=False, capture_output=True,
                text=True,
            ).stdout.strip(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests / total_tests) * 100:.1f}%"
                if total_tests > 0
                else "0%",
                "total_duration": f"{total_duration:.2f}s",
                "env_file_available": self.env_available,
                "strict_mode": self.strict,
            },
            "coverage": coverage_data.get("totals", {}),
            "test_results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "duration": f"{r.duration:.2f}s",
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in self.results
            ],
            "failed_tests": [
                {
                    "name": r.name,
                    "details": r.details,
                    "duration": f"{r.duration:.2f}s",
                }
                for r in self.results
                if not r.success
            ],
        }

        # Write report
        report_file = REPORTS_DIR / "comprehensive_test_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Print summary
        print()
        print("=" * 80)
        print("🏁 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        print(
            f"📊 Tests: {passed_tests}/{total_tests} passed "
            f"({report['summary']['success_rate']})"
        )
        print(f"⏱️  Duration: {total_duration:.2f}s")
        print(f"🐍 Python: {report['python_version']}")
        print(f"📄 .env: {'Available' if self.env_available else 'Not found'}")

        if coverage_data:
            coverage_percent = coverage_data.get("percent_covered", 0)
            print(f"📈 Coverage: {coverage_percent:.1f}%")

        print(f"📋 Report: {report_file}")

        if failed_tests > 0:
            print()
            print("❌ FAILED TESTS:")
            for result in self.results:
                if not result.success:
                    print(f"   • {result.name}")

        print("=" * 80)

    def run_all(self, skip_e2e: bool = False, skip_performance: bool = False) -> bool:
        """Run all tests and quality checks."""
        print("🔧 Running comprehensive test suite...")
        print()

        # Quality checks first
        self.results.append(self.lint_test_files())
        self.results.append(self.type_check_test_files())
        self.results.append(self.run_linting())
        self.results.append(self.run_formatting_check())
        self.results.append(self.run_type_checking())
        self.results.append(self.run_security_analysis())

        # Core tests
        self.results.append(self.run_unit_tests())
        self.results.append(self.run_integration_tests())

        if not skip_e2e:
            self.results.append(self.run_e2e_tests())

        if not skip_performance:
            self.results.append(self.run_performance_tests())

        # Generate reports
        self.results.append(self.generate_coverage_report())

        self.generate_final_report()

        # Return overall success
        all_critical_passed = all(
            r.success
            for r in self.results
            if r.name
            in [
                "Ruff Linting (Strict)",
                "MyPy Type Checking (Strict)",
                "Unit Tests + Coverage",
                "Test Files Linting",
                "Test Files Type Checking",
            ]
        )

        return all_critical_passed


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Modern test runner for client-a OUD Migration",
    )
    parser.add_argument("--no-strict", action="store_true", help="Disable strict mode")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    parser.add_argument("--skip-e2e", action="store_true", help="Skip E2E tests")
    parser.add_argument(
        "--skip-performance", action="store_true", help="Skip performance tests",
    )
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--lint-only", action="store_true", help="Run only linting checks",
    )

    args = parser.parse_args()

    # Verify Python and tools
    if not VENV_PYTHON.exists():
        print(f"❌ Python not found at {VENV_PYTHON}")
        return 1

    for tool in [PYTEST, RUFF, MYPY]:
        if not tool.exists():
            print(f"❌ Tool not found: {tool}")
            return 1

    runner = ModernTestRunner(
        verbose=not args.quiet,
        strict=not args.no_strict,
    )

    try:
        if args.unit_only:
            runner.results.append(runner.run_unit_tests())
            success = runner.results[-1].success
        elif args.lint_only:
            runner.results.append(runner.run_linting())
            runner.results.append(runner.run_type_checking())
            success = all(r.success for r in runner.results)
        else:
            success = runner.run_all(
                skip_e2e=args.skip_e2e,
                skip_performance=args.skip_performance,
            )

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n❌ Test run interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test run failed with exception: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
