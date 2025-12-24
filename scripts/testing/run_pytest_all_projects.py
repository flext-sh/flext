"""FLEXT Pytest Runner - Execute pytest across all workspace projects with timeout.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Constants
TIMEOUT_SECONDS = 300  # 5 minutes per test suite
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEST_RESULTS_DIR = PROJECT_ROOT / "test-results" / "pytest"
VENV_PATH = PROJECT_ROOT / ".venv" / "bin" / "activate"

# Project hierarchy based on FLEXT architecture
PROJECT_HIERARCHY = {
    "tier0": ["flext-core"],
    "tier1": [
        "flext-cli",
        "flext-observability",
        "flext-grpc",
        "flext-web",
        "flext-api",
        "flext-auth",
    ],
    "tier2": [
        "flext-meltano",
        "flext-ldif",
        "flext-ldap",
        "flext-db-oracle",
        "flext-oracle-wms",
        "flext-oracle-oic",
    ],
    "tier3": [
        "flext-tap-ldap",
        "flext-tap-ldif",
        "flext-tap-oracle",
        "flext-tap-oracle-oic",
        "flext-tap-oracle-wms",
        "flext-target-ldap",
        "flext-target-ldif",
        "flext-target-oracle",
        "flext-target-oracle-oic",
        "flext-target-oracle-wms",
        "flext-dbt-ldap",
        "flext-dbt-ldif",
        "flext-dbt-oracle",
        "flext-dbt-oracle-wms",
        "flext-plugin",
        "flext-quality",
    ],
    "special": ["client-a-oud-mig", "client-b-meltano-native", "flexcore"],
}


class FLEXTTestRunner:
    """FLEXT Test Runner for systematic pytest execution."""

    def __init__(self) -> None:
        """Initialize the FLEXT test runner."""
        self.results = {}
        self.failed_projects = []
        TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}", flush=True)

    def get_project_path(self, project_name: str) -> Path:
        """Get full path to project."""
        if project_name == "flexcore":
            return PROJECT_ROOT / project_name
        return PROJECT_ROOT / f"{project_name}"

    def run_pytest_with_timeout(
        self,
        project_path: Path,
        timeout: int = TIMEOUT_SECONDS,
    ) -> tuple[int, str, str]:
        """Run pytest with timeout and capture output."""
        try:
            cmd = [
                "python",
                "-m",
                "pytest",
                "--tb=short",
                "--strict-markers",
                "--disable-warnings",
                "-x",  # Stop on first failure
                "--timeout=60",  # 60 seconds per test
                "tests/",
            ]

            self.log(f"Running pytest in {project_path}")
            self.log(f"Command: {' '.join(cmd)}")

            # Change to project directory and run
            result = subprocess.run(
                cmd,
                check=False,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, "PYTHONPATH": str(project_path / "src")},
            )

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return -1, "", f"Test execution timed out after {timeout} seconds"
        except Exception as e:
            return -2, "", f"Failed to run tests: {e}"

    def save_test_results(
        self,
        project_name: str,
        returncode: int,
        stdout: str,
        stderr: str,
    ) -> None:
        """Save test results to files."""
        project_results_dir = TEST_RESULTS_DIR / project_name
        project_results_dir.mkdir(parents=True, exist_ok=True)

        # Save stdout
        Path(project_results_dir / "stdout.log").write_text(stdout, encoding="utf-8")

        # Save stderr
        Path(project_results_dir / "stderr.log").write_text(stderr, encoding="utf-8")

        # Save summary
        summary = {
            "project": project_name,
            "returncode": returncode,
            "timestamp": time.time(),
            "has_stdout": len(stdout.strip()) > 0,
            "has_stderr": len(stderr.strip()) > 0,
            "stdout_lines": len(stdout.splitlines()),
            "stderr_lines": len(stderr.splitlines()),
        }

        with Path(project_results_dir / "summary.json").open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(summary, f, indent=2)

    def run_project_tests(self, project_name: str) -> bool:
        """Run tests for a single project."""
        project_path = self.get_project_path(project_name)

        if not project_path.exists():
            self.log(f"Project directory not found: {project_path}", "WARNING")
            return False

        if not (project_path / "tests").exists():
            self.log(f"No tests directory found in {project_name}", "WARNING")
            return True  # Not a failure, just no tests

        self.log(f"🧪 Testing {project_name}...")

        returncode, stdout, stderr = self.run_pytest_with_timeout(project_path)

        # Save results
        self.save_test_results(project_name, returncode, stdout, stderr)

        if returncode == 0:
            self.log(f"✅ {project_name} tests PASSED", "SUCCESS")
            return True
        self.log(f"❌ {project_name} tests FAILED (exit code: {returncode})", "ERROR")
        self.failed_projects.append(project_name)

        # Log first few lines of error output
        if stderr:
            error_lines = stderr.splitlines()[:10]
            self.log("Error output (first 10 lines):", "ERROR")
            for line in error_lines:
                self.log(f"  {line}", "ERROR")

        return False

    def run_tier_tests(self, tier_name: str, projects: list[str]) -> list[str]:
        """Run tests for all projects in a tier."""
        self.log(f"🏗️  Running {tier_name} tests...")
        return [project for project in projects if not self.run_project_tests(project)]

    async def run_all_tests(self) -> dict[str, list[str]]:
        """Run tests for all projects in hierarchical order."""
        self.log("🚀 Starting FLEXT Pytest Suite...")
        self.log("=" * 50)

        all_failed = {}

        # Tier 0 - Foundation (must pass first)
        tier0_failed = self.run_tier_tests(
            "Tier 0 (Foundation)",
            PROJECT_HIERARCHY["tier0"],
        )
        all_failed["tier0"] = tier0_failed

        # Only continue if foundation passes
        if tier0_failed:
            self.log("❌ Foundation tier failed - stopping execution", "ERROR")
            return all_failed

        # Tier 1 - Domain Foundation
        tier1_failed = self.run_tier_tests(
            "Tier 1 (Domain Foundation)",
            PROJECT_HIERARCHY["tier1"],
        )
        all_failed["tier1"] = tier1_failed

        # Tier 2 - Infrastructure
        tier2_failed = self.run_tier_tests(
            "Tier 2 (Infrastructure)",
            PROJECT_HIERARCHY["tier2"],
        )
        all_failed["tier2"] = tier2_failed

        # Tier 3 - Application
        tier3_failed = self.run_tier_tests(
            "Tier 3 (Application)",
            PROJECT_HIERARCHY["tier3"],
        )
        all_failed["tier3"] = tier3_failed

        # Special projects
        special_failed = self.run_tier_tests(
            "Special Projects",
            PROJECT_HIERARCHY["special"],
        )
        all_failed["special"] = special_failed

        # Generate final report
        self.generate_final_report(all_failed)

        return all_failed

    def generate_final_report(self, results: dict[str, list[str]]) -> None:
        """Generate comprehensive test report."""
        report_path = TEST_RESULTS_DIR / "final_report.json"

        total_projects = sum(len(projects) for projects in PROJECT_HIERARCHY.values())
        failed_projects = [p for tier_failed in results.values() for p in tier_failed]
        passed_projects = total_projects - len(failed_projects)

        report = {
            "timestamp": time.time(),
            "total_projects": total_projects,
            "passed_projects": passed_projects,
            "failed_projects": failed_projects,
            "success_rate": f"{(passed_projects / total_projects) * 100:.1f}%"
            if total_projects > 0
            else "0%",
            "results_by_tier": results,
            "failed_project_list": failed_projects,
        }

        with Path(report_path).open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        self.log("=" * 50)
        self.log("📊 FLEXT TEST REPORT")
        self.log("=" * 50)
        self.log(f"Total Projects: {total_projects}")
        self.log(f"Passed: {passed_projects}")
        self.log(f"Failed: {len(failed_projects)}")
        self.log(f"Success Rate: {report['success_rate']}")
        self.log(f"Report saved: {report_path}")

        if failed_projects:
            self.log("❌ Failed Projects:", "ERROR")
            for project in failed_projects:
                self.log(f"  - {project}", "ERROR")


def main() -> None:
    """Main entry point."""
    # Ensure we're in the right environment
    if not VENV_PATH.exists():
        print("❌ Virtual environment not found. Please run from FLEXT workspace root.")
        sys.exit(1)

    runner = FLEXTTestRunner()

    try:
        # Run all tests asynchronously to avoid blocking
        results = asyncio.run(runner.run_all_tests())

        # Exit with failure if any tests failed
        failed_count = sum(len(failed) for failed in results.values())
        if failed_count > 0:
            print(f"\n❌ {failed_count} test suites failed")
            sys.exit(1)
        else:
            print("\n🎉 All tests passed!")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
