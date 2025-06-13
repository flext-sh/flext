#!/usr/bin/env python3
"""Comprehensive Test Runner for FLX Project.
Executes all possible tests across all FLX modules with detailed reporting.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import sys
import time
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class FlxTestConfig(BaseModel):
    """Configuration for FLX test execution."""

    model_config = ConfigDict(strict=True, extra="forbid")

    # Test directories to scan
    test_directories: list[str] = Field(
        default=[
            "flx/tests",
            "flx_database_oracle/tests",
            "flx_http_oracle_wms/tests",
            "flx_http_oracle_oic/tests",
            "dc-oracle-wms/tests",
            "dc-oracle-db/tests",
            "tests",
        ],
        description="Directories containing tests",
    )

    # Test categories to run
    test_categories: list[str] = Field(
        default=[
            "unit",
            "integration",
            "performance",
            "security",
            "smoke",
            "e2e",
        ],
        description="Test categories to execute",
    )

    # Pytest options
    pytest_options: list[str] = Field(
        default=[
            "--verbose",
            "--tb=short",
            "--color=yes",
            "--durations=10",
            "--maxfail=10",
            "--disable-warnings",
        ],
        description="Pytest command line options",
    )

    # Coverage options
    enable_coverage: bool = Field(default=True, description="Enable coverage reporting")
    coverage_threshold: float = Field(default=80.0, description="Minimum coverage threshold")

    # Parallel execution
    parallel_workers: int = Field(default=4, description="Number of parallel test workers")

    # Output options
    generate_html_report: bool = Field(default=True, description="Generate HTML test report")
    generate_json_report: bool = Field(default=True, description="Generate JSON test report")
    generate_junit_xml: bool = Field(default=True, description="Generate JUnit XML report")

    # Timeout settings
    test_timeout: int = Field(default=300, description="Test timeout in seconds")


class FlxTestResult(BaseModel):
    """Result of FLX test execution."""

    model_config = ConfigDict(strict=True, extra="forbid")

    project_name: str = Field(description="Name of the tested flx_project")
    test_category: str = Field(description="Category of tests executed")
    total_tests: int = Field(description="Total number of tests")
    passed_tests: int = Field(description="Number of passed tests")
    failed_tests: int = Field(description="Number of failed tests")
    skipped_tests: int = Field(description="Number of skipped tests")
    execution_time: float = Field(description="Execution time in seconds")
    coverage_percentage: float | None = Field(default=None, description="Code coverage percentage")
    success: bool = Field(description="Whether all tests passed")
    error_message: str | None = Field(default=None, description="Error message if failed")
    output_files: list[str] = Field(default_factory=list, description="Generated output files")


class FlxTestRunner:
    """Comprehensive test runner for FLX flx_project."""

    def __init__(self, config: FlxTestConfig) -> None:
        """Initialize test runner with configuration."""
        self.config = config
        self.results: list[FlxTestResult] = []
        self.start_time = time.time()

        # Ensure output directories exist
        self._setup_output_directories()

    def _setup_output_directories(self) -> None:
        """Create necessary output directories."""
        directories = [
            "reports/pytest",
            "reports/coverage",
            "junit",
            "logs/testing",
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    async def run_all_tests(self) -> list[FlxTestResult]:
        """Run all possible tests across all FLX projects."""
        print("🚀 Starting comprehensive FLX test execution...")
        print(f"📊 Configuration: {len(self.config.test_directories)} projects, {len(self.config.test_categories)} categories")

        # Run tests for each flx_project and category combination
        tasks = []
        for project_dir in self.config.test_directories:
            if Path(project_dir).exists():
                for category in self.config.test_categories:
                    task = self._run_project_tests(project_dir, category)
                    tasks.append(task)

        # Execute tests in parallel batches
        batch_size = self.config.parallel_workers
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, FlxTestResult):
                    self.results.append(result)
                elif isinstance(result, Exception):
                    print(f"❌ Error in test execution: {result}")

        # Generate comprehensive reports
        await self._generate_reports()

        return self.results

    async def _run_project_tests(self, project_dir: str, category: str) -> FlxTestResult:
        """Run tests for a specific flx_project and category."""
        project_name = Path(project_dir).name
        print(f"🧪 Running {category} tests for {project_name}...")

        start_time = time.time()

        # Build pytest command
        cmd = self._build_pytest_command(project_dir, category)

        try:
            # Execute tests
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path.cwd(),
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.test_timeout,
            )

            execution_time = time.time() - start_time

            # Parse test results
            result = self._parse_test_output(
                project_name, category, stdout.decode(), stderr.decode(),
                process.returncode, execution_time,
            )

            status_emoji = "✅" if result.success else "❌"
            print(f"{status_emoji} {project_name} {category}: {result.passed_tests}/{result.total_tests} passed ({execution_time:.2f}s)")

            return result

        except TimeoutError:
            execution_time = time.time() - start_time
            print(f"⏰ Timeout: {project_name} {category} tests exceeded {self.config.test_timeout}s")

            return FlxTestResult(
                project_name=project_name,
                test_category=category,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=execution_time,
                success=False,
                error_message=f"Test execution timed out after {self.config.test_timeout}s",
            )

        except Exception as e:
            execution_time = time.time() - start_time
            print(f"💥 Error running {project_name} {category} tests: {e}")

            return FlxTestResult(
                project_name=project_name,
                test_category=category,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                execution_time=execution_time,
                success=False,
                error_message=str(e),
            )

    def _build_pytest_command(self, project_dir: str, category: str) -> list[str]:
        """Build pytest command for specific flx_project and category."""
        cmd = ["python", "-m", "pytest"]

        # Add flx_project directory
        cmd.append(project_dir)

        # Add category marker
        cmd.extend(["-m", category])

        # Add pytest options
        cmd.extend(self.config.pytest_options)

        # Add coverage if enabled
        if self.config.enable_coverage:
            cmd.extend([
                "--cov=flx",
                "--cov=wms",
                "--cov=db",
                "--cov=oic",
                f"--cov-report=html:reports/coverage/{project_dir.replace('/', '_')}_{category}",
                f"--cov-report=xml:reports/coverage/{project_dir.replace('/', '_')}_{category}.xml",
                "--cov-report=term-missing",
            ])

        # Add output files
        if self.config.generate_junit_xml:
            cmd.extend([f"--junit-xml=junit/{project_dir.replace('/', '_')}_{category}.xml"])

        if self.config.generate_html_report:
            cmd.extend([f"--html=reports/pytest/{project_dir.replace('/', '_')}_{category}.html", "--self-contained-html"])

        return cmd

    def _parse_test_output(
        self,
        project_name: str,
        category: str,
        stdout: str,
        stderr: str,
        return_code: int,
        execution_time: float,
    ) -> FlxTestResult:
        """Parse pytest output to extract test results."""
        # Initialize counters
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        coverage_percentage = None

        # Parse stdout for test results
        lines = stdout.split("\n")
        for line in lines:
            # Look for test summary line
            if "passed" in line or "failed" in line or "skipped" in line:
                # Extract numbers from lines like "5 passed, 2 failed, 1 skipped"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit():
                        count = int(part)
                        if i + 1 < len(parts):
                            next_word = parts[i + 1]
                            if "passed" in next_word:
                                passed_tests = count
                            elif "failed" in next_word:
                                failed_tests = count
                            elif "skipped" in next_word:
                                skipped_tests = count

            # Look for coverage percentage
            if "TOTAL" in line and "%" in line:
                parts = line.split()
                for part in parts:
                    if "%" in part:
                        with contextlib.suppress(ValueError):
                            coverage_percentage = float(part.replace("%", ""))

        total_tests = passed_tests + failed_tests + skipped_tests

        # Determine success
        success = return_code == 0 and failed_tests == 0

        # Extract error message if failed
        error_message = None
        if not success:
            if stderr:
                error_message = stderr[:500]  # Truncate long error messages
            elif "FAILED" in stdout:
                # Extract first failure message
                failure_lines = [line for line in lines if "FAILED" in line]
                if failure_lines:
                    error_message = failure_lines[0][:500]

        return FlxTestResult(
            project_name=project_name,
            test_category=category,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            execution_time=execution_time,
            coverage_percentage=coverage_percentage,
            success=success,
            error_message=error_message,
        )

    async def _generate_reports(self) -> None:
        """Generate comprehensive test reports."""
        print("\n📊 Generating comprehensive test reports...")

        # Generate JSON report
        if self.config.generate_json_report:
            await self._generate_json_report()

        # Generate summary report
        await self._generate_summary_report()

        # Generate markdown report
        await self._generate_markdown_report()

    async def _generate_json_report(self) -> None:
        """Generate JSON test report."""
        report_data = {
            "execution_summary": {
                "total_execution_time": time.time() - self.start_time,
                "total_projects": len({r.project_name for r in self.results}),
                "total_categories": len({r.test_category for r in self.results}),
                "total_test_runs": len(self.results),
                "successful_runs": len([r for r in self.results if r.success]),
                "failed_runs": len([r for r in self.results if not r.success]),
            },
            "test_results": [result.model_dump() for result in self.results],
            "configuration": self.config.model_dump(),
        }

        report_file = Path("reports/pytest/comprehensive_test_report.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        print(f"📄 JSON report generated: {report_file}")

    async def _generate_summary_report(self) -> None:
        """Generate summary test report."""
        total_tests = sum(r.total_tests for r in self.results)
        total_passed = sum(r.passed_tests for r in self.results)
        total_failed = sum(r.failed_tests for r in self.results)
        total_skipped = sum(r.skipped_tests for r in self.results)
        total_time = time.time() - self.start_time

        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "=" * 80)
        print("🎯 COMPREHENSIVE FLX TEST EXECUTION SUMMARY")
        print("=" * 80)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_failed}")
        print(f"⏭️  Skipped: {total_skipped}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print()

        # Project breakdown
        print("📋 PROJECT BREAKDOWN:")
        projects = {}
        for result in self.results:
            if result.project_name not in projects:
                projects[result.project_name] = {
                    "total": 0, "passed": 0, "failed": 0, "skipped": 0,
                }
            projects[result.project_name]["total"] += result.total_tests
            projects[result.project_name]["passed"] += result.passed_tests
            projects[result.project_name]["failed"] += result.failed_tests
            projects[result.project_name]["skipped"] += result.skipped_tests

        for flx_project, stats in projects.items():
            if stats["total"] > 0:
                project_success = stats["passed"] / stats["total"] * 100
                print(f"  {flx_project}: {stats['passed']}/{stats['total']} ({project_success:.1f}%)")

        print("\n" + "=" * 80)

    async def _generate_markdown_report(self) -> None:
        """Generate markdown test report."""
        total_time = time.time() - self.start_time

        markdown_content = f"""# FLX Comprehensive Test Report

## Execution Summary
- **Total Execution Time**: {total_time:.2f} seconds
- **Projects Tested**: {len({r.project_name for r in self.results})}
- **Test Categories**: {len({r.test_category for r in self.results})}
- **Total Test Runs**: {len(self.results)}

## Results Overview

| Project | Category | Tests | Passed | Failed | Skipped | Coverage | Status |
|---------|----------|-------|--------|--------|---------|----------|--------|
"""

        for result in self.results:
            status_emoji = "✅" if result.success else "❌"
            coverage_str = f"{result.coverage_percentage:.1f}%" if result.coverage_percentage else "N/A"

            markdown_content += f"| {result.project_name} | {result.test_category} | {result.total_tests} | {result.passed_tests} | {result.failed_tests} | {result.skipped_tests} | {coverage_str} | {status_emoji} |\n"

        # Add failure details
        failed_results = [r for r in self.results if not r.success]
        if failed_results:
            markdown_content += "\n## Failed Tests Details\n\n"
            for result in failed_results:
                markdown_content += f"### {result.project_name} - {result.test_category}\n"
                if result.error_message:
                    markdown_content += f"```\n{result.error_message}\n```\n\n"

        report_file = Path("reports/pytest/comprehensive_test_report.md")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"📄 Markdown report generated: {report_file}")


async def main() -> None:
    """Main entry point for test runner."""
    print("🔬 FLX Comprehensive Test Runner")
    print("=" * 50)

    # Load configuration
    config = FlxTestConfig()

    # Create and run test runner
    runner = FlxTestRunner(config)
    results = await runner.run_all_tests()

    # Exit with appropriate code
    failed_runs = [r for r in results if not r.success]
    if failed_runs:
        print(f"\n❌ {len(failed_runs)} test runs failed")
        sys.exit(1)
    else:
        print("\n✅ All test runs completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
