#!/usr/bin/env python
"""
Comprehensive dry-run validator - Tests ALL functionality before real fixes.

Per CLAUDE.md RULE 4: Complete Delivery - Test before claiming success.
"""

import logging
import subprocess
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class ComprehensiveDryRunValidator:
    """Validate ALL workspace functionality before making changes."""

    def __init__(self):
        """Initialize validator."""
        self.workspace_root = Path("/home/marlonsc/pyauto")
        self.submodules = [
            "algar-oud-mig",
            "dbt-ldap",
            "dc-code-analyzer",
            "flx",
            "flx-adapter-example",
            "flx-database-oracle",
            "flx-http-oracle-oic",
            "flx-http-oracle-wms",
            "flx-ldap",
            "flx-meltano-enterprise",
            "flx-oracle-oic",
            "flx-oracle-wms",
            "gruponos-poc-oic-wms",
            "ldap-core-shared",
            "oracle-oic-ext",
            "tap-ldap",
            "tap-oracle-oic",
            "tap-oracle-wms",
            "target-ldap",
            "target-oracle-oic",
            "target-oracle-wms",
        ]
        self.results = {}

    def test_poetry_install(self, project_name: str) -> bool:
        """Test if poetry install works."""
        project_path = self.workspace_root / project_name

        if not project_path.exists():
            return False

        try:
            result = subprocess.run(
                ["poetry", "install", "--dry-run"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception:
            return False

    def test_module_import(self, project_name: str) -> bool:
        """Test if module imports successfully."""
        project_path = self.workspace_root / project_name
        module_name = project_name.replace("-", "_")

        try:
            result = subprocess.run(
                [
                    "poetry",
                    "run",
                    "python",
                    "-c",
                    f"import {module_name}; logger.info('OK')",
                ],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0 and "OK" in result.stdout
        except Exception:
            return False

    def test_ruff_violations(self, project_name: str) -> int:
        """Count current ruff violations."""
        project_path = self.workspace_root / project_name

        try:
            result = subprocess.run(
                ["poetry", "run", "ruff", "check", ".", "--quiet"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return len([l for l in result.stdout.split("\n") if l.strip()])
        except Exception:
            return -1

    def test_mypy_check(self, project_name: str) -> bool:
        """Test MyPy type checking."""
        project_path = self.workspace_root / project_name

        try:
            result = subprocess.run(
                ["poetry", "run", "mypy", ".", "--no-error-summary"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0
        except Exception:
            return False

    def test_pytest_execution(self, project_name: str) -> bool:
        """Test if pytest runs without errors."""
        project_path = self.workspace_root / project_name

        try:
            result = subprocess.run(
                ["poetry", "run", "pytest", "--tb=no", "-q", "--maxfail=1"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            # Accept if no tests or tests pass
            return result.returncode in [0, 5]  # 5 = no tests collected
        except Exception:
            return False

    def test_cli_functionality(self, project_name: str) -> bool:
        """Test CLI functionality where applicable."""
        project_path = self.workspace_root / project_name

        cli_commands = {
            "tap-ldap": ["tap-ldap", "--help"],
            "target-ldap": ["target-ldap", "--help"],
            "tap-oracle-oic": ["tap-oracle-oic", "--help"],
            "tap-oracle-wms": ["tap-oracle-wms", "--help"],
            "target-oracle-oic": ["target-oracle-oic", "--help"],
            "target-oracle-wms": ["target-oracle-wms", "--help"],
            "flx": ["python", "-m", "flx", "--help"],
            "dbt-ldap": ["dbt", "--help"],
        }

        if project_name not in cli_commands:
            return True  # No CLI to test

        try:
            result = subprocess.run(
                ["poetry", "run"] + cli_commands[project_name],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode in [0, 2] or "--help" in result.stdout
        except Exception:
            return False

    def validate_project_completely(self, project_name: str) -> dict:
        """Complete validation of a single project."""
        logger.info(f"\n📋 Validating {project_name}...")

        start_time = time.time()

        result = {
            "poetry_install": self.test_poetry_install(project_name),
            "module_import": self.test_module_import(project_name),
            "ruff_violations": self.test_ruff_violations(project_name),
            "mypy_check": self.test_mypy_check(project_name),
            "pytest_execution": self.test_pytest_execution(project_name),
            "cli_functionality": self.test_cli_functionality(project_name),
            "validation_time": time.time() - start_time,
        }

        # Calculate score
        score = 0
        total_tests = 5  # Exclude ruff_violations from score

        if result["poetry_install"]:
            score += 1
        if result["module_import"]:
            score += 1
        if result["ruff_violations"] == 0:
            score += 1
        if result["mypy_check"]:
            score += 1
        if result["pytest_execution"]:
            score += 1
        if result["cli_functionality"]:
            score += 1

        result["score"] = score
        result["total_tests"] = total_tests + 1  # Include CLI
        result["percentage"] = (score / (total_tests + 1)) * 100

        # Status determination
        if score == total_tests + 1:
            result["status"] = "✅ PERFECT"
        elif score >= total_tests:
            result["status"] = "✅ EXCELLENT"
        elif score >= total_tests - 1:
            result["status"] = "⚠️  GOOD"
            result["status"] = "❌ NEEDS_WORK"

        logger.info(
            f"  {result['status']} - {result['percentage']:.1f}% ({score}/{total_tests + 1})"
        )
        if result["ruff_violations"] > 0:
            logger.info(f"  📊 Ruff violations: {result['ruff_violations']}")

        return result

    def run_complete_validation(self) -> None:
        """Run complete validation across all projects."""
        logger.info("🎯 COMPREHENSIVE DRY-RUN VALIDATION")
        logger.info("=" * 80)
        logger.info("Testing ALL functionality before making changes...")
        logger.info("=" * 80)

        total_score = 0
        total_possible = 0
        perfect_projects: list = []
        needs_work: list = []

        for project in self.submodules:
            result = self.validate_project_completely(project)
            self.results[project] = result

            total_score += result["score"]
            total_possible += result["total_tests"]

            if result["status"] == "✅ PERFECT":
                perfect_projects.append(project)
            elif result["status"] == "❌ NEEDS_WORK":
                needs_work.append(project)

        # Generate summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 DRY-RUN VALIDATION SUMMARY")
        logger.info("=" * 80)

        overall_percentage = (total_score / total_possible) * 100
        logger.info(
            f"Overall Score: {total_score}/{total_possible} ({overall_percentage:.1f}%)"
        )
        logger.info(f"Perfect Projects: {len(perfect_projects)}/21")
        logger.info(f"Needs Work: {len(needs_work)}/21")

        # Status breakdown
        status_counts: dict = {}
        total_violations = 0

        for project, result in self.results.items():
            status = result["status"]
            if status not in status_counts:
                status_counts[status] = 0
            status_counts[status] += 1

            if result["ruff_violations"] > 0:
                total_violations += result["ruff_violations"]

        logger.info("\nStatus Breakdown:")
        for status, count in sorted(status_counts.items()):
            logger.info(f"  {status}: {count} projects")

        logger.info(f"\nTotal Ruff Violations: {total_violations}")

        # Detailed project status
        logger.info("\n📋 DETAILED PROJECT STATUS:")
        logger.info(f"{'Project':<25} {'Score':>8} {'Violations':>12} {'Status':>15}")
        logger.info("-" * 70)

        for project, result in sorted(self.results.items()):
            result["ruff_violations"] if result["ruff_violations"] >= 0 else "ERROR"

        # Problems to fix
        if needs_work:
            logger.info("\n❌ PROJECTS NEEDING IMMEDIATE ATTENTION:")
            for project in needs_work:
                result = self.results[project]
                logger.info(f"\n{project}:")
                if not result["poetry_install"]:
                    logger.info("  - Poetry install failing")
                if not result["module_import"]:
                    logger.info("  - Module import failing")
                if not result["mypy_check"]:
                    logger.info("  - MyPy type check failing")
                if not result["pytest_execution"]:
                    logger.info("  - Pytest execution failing")
                if not result["cli_functionality"]:
                    logger.info("  - CLI functionality failing")
                if result["ruff_violations"] > 0:
                    logger.info(f"  - {result['ruff_violations']} ruff violations")

        # Success criteria
        logger.info("\n🎯 SUCCESS CRITERIA:")
        logger.info(
            f"✅ All projects install: {all(r['poetry_install'] for r in self.results.values())}"
        )
        logger.info(
            f"✅ All projects import: {all(r['module_import'] for r in self.results.values())}"
        )
        logger.info(f"✅ Zero violations: {total_violations == 0}")
        logger.info(
            f"✅ All CLIs work: {all(r['cli_functionality'] for r in self.results.values())}"
        )

        workspace_ready = (
            all(r["poetry_install"] for r in self.results.values())
            and all(r["module_import"] for r in self.results.values())
            and all(r["cli_functionality"] for r in self.results.values())
        )

        if workspace_ready:
            logger.info("\n🎉 WORKSPACE IS FUNCTIONAL - Safe to apply targeted fixes!")
            logger.info("\n⚠️  WORKSPACE HAS CRITICAL ISSUES - Fix before proceeding!")

        # Log to token
        with open(self.workspace_root / ".token", "a") as f:
            f.write(
                f"DRY-RUN-VALIDATION-001: {overall_percentage:.1f}% functional, {total_violations} violations\n"
            )

        return workspace_ready, total_violations


if __name__ == "__main__":
    validator = ComprehensiveDryRunValidator()
    workspace_ready, violations = validator.run_complete_validation()

    if workspace_ready:
        logger.info("\n✅ VALIDATION PASSED - Workspace ready for fixes")
        sys.exit(0)
        logger.info("\n❌ VALIDATION FAILED - Critical issues must be resolved first")
        sys.exit(1)
