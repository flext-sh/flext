#!/usr/bin/env python3
"""Quick Test Runner for FLX Project Development.
Provides fast testing for development with simplified output.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class QuickTestConfig(BaseModel):
    """Configuration for quick test execution."""

    model_config = ConfigDict(strict=True, extra="forbid")

    flx_project: str | None = Field(
        default=None,
        description="Specific flx_project to test",
    )
    category: str = Field(default="unit", description="Test category to run")
    verbose: bool = Field(default=False, description="Verbose output")
    fail_fast: bool = Field(default=True, description="Stop on first failure")
    coverage: bool = Field(default=False, description="Enable coverage")
    timeout: int = Field(default=60, description="Test timeout in seconds")


class QuickTestRunner:
    """Quick test runner for development."""

    def __init__(self, config: QuickTestConfig) -> None:
        """Initialize quick test runner."""
        self.config = config
        self.available_projects = [
            "flx/tests",
            "flx_database_oracle/tests",
            "flx_http_oracle_wms/tests",
            "flx_http_oracle_oic/tests",
            "dc-oracle-wms/tests",
            "dc-oracle-db/tests",
        ]

    def run_tests(self) -> bool:
        """Run quick tests."""
        print("⚡ FLX Quick Test Runner")
        print("-" * 30)

        if self.config.flx_project:
            # Test specific flx_project
            project_path = self._find_project_path(self.config.flx_project)
            if not project_path:
                print(f"❌ Project '{self.config.flx_project}' not found")
                return False

            return self._run_project_test(project_path)
        # Test all available projects
        success = True
        for project_path in self.available_projects:
            if Path(project_path).exists():
                if not self._run_project_test(project_path):
                    success = False
                    if self.config.fail_fast:
                        break
        return success

    def _find_project_path(self, project_name: str) -> str | None:
        """Find flx_project path by name."""
        for project_path in self.available_projects:
            if project_name in project_path:
                return project_path
        return None

    def _run_project_test(self, project_path: str) -> bool:
        """Run tests for a specific flx_project."""
        project_name = Path(project_path).name
        print(f"🧪 Testing {project_name} ({self.config.category})...")

        start_time = time.time()

        # Build command
        cmd = self._build_command(project_path)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
                check=False,
            )

            duration = time.time() - start_time

            # Parse results
            success = result.returncode == 0
            passed, failed, _skipped = self._parse_output(result.stdout)

            # Display results
            if success:
                print(f"✅ {project_name}: {passed} passed ({duration:.1f}s)")
                print(
                    f"❌ {project_name}: {failed} failed, {passed} passed ({
                        duration:.1f
                    }s)",
                )
                if self.config.verbose and result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")

            return success

        except subprocess.TimeoutExpired:
            print(f"⏰ {project_name}: Timeout after {self.config.timeout}s")
            return False
        except Exception as e:
            print(f"💥 {project_name}: Error - {e}")
            return False

    def _build_command(self, project_path: str) -> list[str]:
        """Build pytest command."""
        cmd = ["python", "-m", "pytest", project_path]

        # Add category marker
        cmd.extend(["-m", self.config.category])

        # Basic options
        if self.config.verbose:
            cmd.append("-v")
            cmd.append("-q")

        if self.config.fail_fast:
            cmd.extend(["-x", "--maxfail=1"])

        # Coverage
        if self.config.coverage:
            cmd.extend(["--cov", "--cov-report=term-missing"])

        # Additional options
        cmd.extend(
            [
                "--tb=short",
                "--disable-warnings",
                "--color=yes",
            ],
        )

        return cmd

    def _parse_output(self, output: str) -> tuple[int, int, int]:
        """Parse test output for counts."""
        passed = output.count(" PASSED") + output.count("✓")
        failed = output.count(" FAILED") + output.count("✗")
        skipped = output.count(" SKIPPED") + output.count("⏭")

        # Try to parse summary line
        lines = output.split("\n")
        for line in lines:
            if "passed" in line and ("failed" in line or "skipped" in line):
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit() and i + 1 < len(parts):
                        count = int(part)
                        next_word = parts[i + 1]
                        if "passed" in next_word:
                            passed = count
                        elif "failed" in next_word:
                            failed = count
                        elif "skipped" in next_word:
                            skipped = count

        return passed, failed, skipped


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Quick test runner for FLX development",
    )
    parser.add_argument(
        "--flx_project",
        "-p",
        help="Specific flx_project to test (flx, oracle, wms, oic, db)",
    )
    parser.add_argument(
        "--category",
        "-c",
        default="unit",
        choices=["unit", "integration", "performance", "security", "smoke", "e2e"],
        help="Test category to run",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--no-fail-fast",
        action="store_true",
        help="Don't stop on first failure",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Enable coverage reporting",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Test timeout in seconds",
    )

    args = parser.parse_args()

    config = QuickTestConfig(
        flx_project=args.flx_project,
        category=args.category,
        verbose=args.verbose,
        fail_fast=not args.no_fail_fast,
        coverage=args.coverage,
        timeout=args.timeout,
    )

    runner = QuickTestRunner(config)
    success = runner.run_tests()

    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
