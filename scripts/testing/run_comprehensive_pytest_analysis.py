#!/usr/bin/env python3
# Owner-Skill: .claude/skills/scripts-testing/SKILL.md
"""Comprehensive FLEXT Pytest Analysis Runner.

Executes pytest across all FLEXT projects with detailed reporting in SARIF and JSON formats.
Generates comprehensive analysis for systematic error fixing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# Constants
TIMEOUT_SECONDS = 600  # 10 minutes per project
PROJECT_ROOT = Path(__file__).parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "test-analysis-output"
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


class PytestAnalyzer:
    """Comprehensive Pytest Analyzer for FLEXT projects."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: dict[str, Any] = {}
        self.sarif_results: list[dict[str, Any]] = []

    def log(self, message: str, level: str = "INFO") -> None:
        """Log message with timestamp."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}", flush=True)

    def get_project_path(self, project_name: str) -> Path:
        """Get full path to project."""
        if project_name == "flexcore":
            return PROJECT_ROOT / project_name
        return PROJECT_ROOT / f"{project_name}"

    def run_pytest_with_analysis(
        self,
        project_path: Path,
        project_name: str,
        timeout: int = TIMEOUT_SECONDS,
    ) -> tuple[int, str, str, dict[str, Any]]:
        """Run pytest with comprehensive analysis and capture detailed results."""
        try:
            # Run pytest with standard output for detailed analysis
            cmd = [
                "python",
                "-m",
                "pytest",
                "--tb=short",
                "--strict-markers",
                "--disable-warnings",
                "--maxfail=50",  # Allow more failures for analysis
                "-v",  # Verbose output
                "--tb=no",  # Minimal traceback for easier parsing
                "tests/",
            ]

            self.log(f"Running comprehensive pytest analysis for {project_name}")

            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
                env={
                    **os.environ,
                    "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",  # Avoid plugin conflicts
                },
            )

            # Parse pytest JSON output from stdout
            pytest_data = self._parse_pytest_output(result.stdout, result.stderr)

            return result.returncode, result.stdout, result.stderr, pytest_data

        except subprocess.TimeoutExpired:
            return -1, "", f"Test execution timed out after {timeout} seconds", {}
        except Exception as e:
            return -2, "", f"Failed to run tests: {e}", {}

    def _parse_pytest_output(self, stdout: str, stderr: str) -> dict[str, Any]:
        """Parse pytest output to extract test results."""
        # Try to extract JSON from pytest output
        lines = stdout.split("\n")
        json_data = {}

        # Look for JSON report lines
        for line in lines:
            if line.strip().startswith("{") and '"report"' in line:
                try:
                    json_data = json.loads(line.strip())
                    break
                except json.JSONDecodeError:
                    continue

        # If no JSON found, parse manually
        if not json_data:
            json_data = self._parse_pytest_manually(stdout, stderr)

        return json_data

    def _parse_pytest_manually(self, stdout: str, stderr: str) -> dict[str, Any]:
        """Manually parse pytest output when JSON is not available."""
        all_lines = stdout.split("\n") + stderr.split("\n")
        passed = 0
        failed = 0
        errors = []
        warnings = []
        test_results = []

        for line in all_lines:
            line = line.strip()

            # Count results and extract test info
            if line.startswith("PASSED"):
                passed += 1
                if "::" in line:
                    test_name = line.split("::")[-1].strip()
                    test_results.append({
                        "nodeid": test_name,
                        "outcome": "passed",
                        "longrepr": None,
                    })
            elif line.startswith(("FAILED", "ERROR")):
                failed += 1
                if "::" in line:
                    test_name = line.split("::")[-1].strip()
                    test_results.append({
                        "nodeid": test_name,
                        "outcome": "failed",
                        "longrepr": line,
                    })
                    errors.append(line)

            # Extract summary from result lines
            elif line.startswith("=") and (
                "failed" in line.lower() or "passed" in line.lower()
            ):
                # Try to extract numbers from summary line
                numbers = re.findall(r"\d+", line)
                if len(numbers) >= 2:
                    if "failed" in line:
                        failed = max(failed, int(numbers[0]))
                        passed = max(passed, int(numbers[1]))
                    elif "passed" in line:
                        passed = max(passed, int(numbers[0]))

            # Collect warnings
            elif "warning" in line.lower():
                warnings.append(line)

        return {
            "summary": {
                "passed": passed,
                "failed": failed,
                "total": passed + failed,
                "errors": errors[:10],  # Limit for readability
                "warnings": warnings[:5],
            },
            "tests": test_results,
            "collected": passed + failed,
        }

    def save_project_results(
        self,
        project_name: str,
        returncode: int,
        stdout: str,
        stderr: str,
        pytest_data: dict[str, Any],
    ) -> None:
        """Save comprehensive project results."""
        project_dir = self.output_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        # Save raw outputs
        (project_dir / "stdout.log").write_text(stdout, encoding="utf-8")
        (project_dir / "stderr.log").write_text(stderr, encoding="utf-8")

        # Save parsed results
        with (project_dir / "pytest_results.json").open("w", encoding="utf-8") as f:
            json.dump(pytest_data, f, indent=2, default=str)

        # Generate SARIF format for this project
        sarif_data = self._generate_sarif_for_project(project_name, pytest_data, stderr)
        with (project_dir / "results.sarif").open("w", encoding="utf-8") as f:
            json.dump(sarif_data, f, indent=2)

        # Summary
        summary = {
            "project": project_name,
            "timestamp": time.time(),
            "exit_code": returncode,
            "pytest_data": pytest_data,
            "has_failures": returncode != 0,
            "error_count": len(
                pytest_data.get("summary", {}).get("error", []),
            ),
            "passed_count": pytest_data.get("summary", {}).get("passed", 0),
            "failed_count": pytest_data.get("summary", {}).get("failed", 0),
        }

        with (project_dir / "summary.json").open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

    def _generate_sarif_for_project(
        self,
        _project_name: str,
        pytest_data: dict[str, Any],
        _stderr: str,
    ) -> dict[str, Any]:
        """Generate SARIF format results for a project."""
        runs = []

        # Extract failures from pytest data
        tests = pytest_data.get("tests", [])
        failures = [t for t in tests if t.get("outcome") == "failed"]

        # Create SARIF run
        run = {
            "tool": {
                "driver": {
                    "name": "pytest",
                    "version": "7.0.0",
                    "informationUri": "https://pytest.org/",
                },
            },
            "results": [],
        }

        for failure in failures:
            result = {
                "ruleId": failure.get("nodeid", "unknown"),
                "level": "error",
                "message": {"text": failure.get("longrepr", "Test failed")},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": failure.get("nodeid", "")},
                        },
                    },
                ],
            }
            run["results"].append(result)

        runs.append(run)

        return {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": runs,
        }

    def analyze_project(self, project_name: str) -> bool:
        """Analyze a single project comprehensively."""
        project_path = self.get_project_path(project_name)

        if not project_path.exists():
            self.log(f"Project directory not found: {project_path}", "WARNING")
            return False

        if not (project_path / "tests").exists():
            self.log(f"No tests directory found in {project_name}", "WARNING")
            return True  # Not a failure, just no tests

        self.log(f"🔍 Analyzing {project_name}...")

        returncode, stdout, stderr, pytest_data = self.run_pytest_with_analysis(
            project_path,
            project_name,
        )

        # Save results
        self.save_project_results(project_name, returncode, stdout, stderr, pytest_data)

        success = returncode == 0
        if success:
            self.log(f"✅ {project_name} analysis completed", "SUCCESS")
        else:
            self.log(f"❌ {project_name} analysis found failures", "ERROR")

        return success

    def generate_consolidated_report(self, all_results: dict[str, list[str]]) -> None:
        """Generate consolidated analysis report."""
        report_path = self.output_dir / "consolidated_analysis.json"
        sarif_path = self.output_dir / "consolidated_results.sarif"

        # Collect all project summaries
        project_summaries = {}
        total_passed = 0
        total_failed = 0
        total_errors = 0

        for project_name in self._get_all_projects():
            summary_path = self.output_dir / project_name / "summary.json"
            if summary_path.exists():
                with summary_path.open("r", encoding="utf-8") as f:
                    summary = json.load(f)
                    project_summaries[project_name] = summary
                    total_passed += summary.get("passed_count", 0)
                    total_failed += summary.get("failed_count", 0)
                    total_errors += summary.get("error_count", 0)

        consolidated = {
            "timestamp": time.time(),
            "analysis_type": "comprehensive_pytest_analysis",
            "total_projects": len(project_summaries),
            "total_passed_tests": total_passed,
            "total_failed_tests": total_failed,
            "total_errors": total_errors,
            "success_rate": f"{(total_passed / max(total_passed + total_failed, 1)) * 100:.1f}%",
            "results_by_tier": all_results,
            "project_summaries": project_summaries,
            "recommendations": self._generate_recommendations(project_summaries),
        }

        # Save consolidated JSON
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(consolidated, f, indent=2)

        # Generate consolidated SARIF
        consolidated_sarif = self._generate_consolidated_sarif(project_summaries)
        with sarif_path.open("w", encoding="utf-8") as f:
            json.dump(consolidated_sarif, f, indent=2)

        self.log("=" * 80)
        self.log("📊 CONSOLIDATED FLEXT PYTEST ANALYSIS REPORT")
        self.log("=" * 80)
        self.log(f"Total Projects: {consolidated['total_projects']}")
        self.log(f"Total Passed Tests: {total_passed}")
        self.log(f"Total Failed Tests: {total_failed}")
        self.log(f"Total Errors: {total_errors}")
        self.log(f"Success Rate: {consolidated['success_rate']}")
        self.log(f"Report saved: {report_path}")
        self.log(f"SARIF Report: {sarif_path}")

        if total_failed > 0 or total_errors > 0:
            self.log("❌ Projects with failures:", "ERROR")
            for project, summary in project_summaries.items():
                if summary.get("has_failures", False):
                    self.log(
                        f"  - {project}: {summary.get('failed_count', 0)} failed, {summary.get('error_count', 0)} errors",
                        "ERROR",
                    )

    def _get_all_projects(self) -> list[str]:
        """Get all projects from hierarchy."""
        all_projects = []
        for projects in PROJECT_HIERARCHY.values():
            all_projects.extend(projects)
        return all_projects

    def _generate_consolidated_sarif(
        self,
        project_summaries: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate consolidated SARIF report."""
        runs = []

        for project_name in project_summaries:
            sarif_path = self.output_dir / project_name / "results.sarif"
            if sarif_path.exists():
                with sarif_path.open("r", encoding="utf-8") as f:
                    project_sarif = json.load(f)
                    runs.extend(project_sarif.get("runs", []))

        return {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": runs,
        }

    def _generate_recommendations(self, project_summaries: dict[str, Any]) -> list[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        failed_projects = [
            name
            for name, summary in project_summaries.items()
            if summary.get("has_failures", False)
        ]

        if failed_projects:
            recommendations.append(
                f"Fix test failures in {len(failed_projects)} projects: {', '.join(failed_projects[:5])}{'...' if len(failed_projects) > 5 else ''}",
            )

            # Prioritize by tier
            tier0_failed = [
                p for p in failed_projects if p in PROJECT_HIERARCHY["tier0"]
            ]
            if tier0_failed:
                recommendations.append(
                    f"🚨 CRITICAL: Fix Tier 0 (Foundation) failures first: {', '.join(tier0_failed)}",
                )

        if len(failed_projects) == 0:
            recommendations.append(
                "🎉 All tests passing! Consider adding more test coverage.",
            )

        return recommendations

    async def run_comprehensive_analysis(self) -> dict[str, list[str]]:
        """Run comprehensive analysis across all projects."""
        self.log("🚀 Starting Comprehensive FLEXT Pytest Analysis...")
        self.log("=" * 80)

        all_failed = {}

        # Process projects in hierarchical order
        tiers = [
            ("Tier 0 (Foundation)", PROJECT_HIERARCHY["tier0"]),
            ("Tier 1 (Domain Foundation)", PROJECT_HIERARCHY["tier1"]),
            ("Tier 2 (Infrastructure)", PROJECT_HIERARCHY["tier2"]),
            ("Tier 3 (Application)", PROJECT_HIERARCHY["tier3"]),
            ("Special Projects", PROJECT_HIERARCHY["special"]),
        ]

        for tier_name, projects in tiers:
            self.log(f"🏗️  Analyzing {tier_name}...")
            failed_projects = []

            for project in projects:
                try:
                    success = await asyncio.get_event_loop().run_in_executor(
                        None,
                        self.analyze_project,
                        project,
                    )
                    if not success:
                        failed_projects.append(project)
                except Exception as e:
                    self.log(f"Error analyzing {project}: {e}", "ERROR")
                    failed_projects.append(project)

            all_failed[tier_name] = failed_projects

        # Generate consolidated report
        self.generate_consolidated_report(all_failed)

        return all_failed


async def main() -> None:
    """Main entry point."""
    # Ensure we're in the right environment
    if not VENV_PATH.exists():
        print("❌ Virtual environment not found. Please run from FLEXT workspace root.")
        sys.exit(1)

    analyzer = PytestAnalyzer()

    try:
        results = await analyzer.run_comprehensive_analysis()

        # Check if any failures
        total_failures = sum(len(failed) for failed in results.values())
        if total_failures > 0:
            print(f"\n❌ Analysis found failures in {total_failures} project tiers")
            print(f"📊 Detailed results saved to: {OUTPUT_DIR}")
            print("🔍 Check consolidated_analysis.json and consolidated_results.sarif")
            sys.exit(1)
        else:
            print("\n🎉 All projects analyzed successfully!")
            print(f"📊 Results saved to: {OUTPUT_DIR}")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
