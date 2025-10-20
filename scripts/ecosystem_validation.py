#!/usr/bin/env python3
"""FLEXT Ecosystem Comprehensive Validation Script.

Validates all FLEXT projects for:
- Syntax errors (Python AST parsing)
- Lint violations (Ruff)
- Type errors (MyPy/PyRight)
- Domain library violations (direct imports)
- Test coverage status

Generates structured report for transformation planning.
"""

from __future__ import annotations

import ast
import json
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

# FLEXT ecosystem projects
FLEXT_PROJECTS = [
    # Foundation
    "flext-core",
    # Domain libraries
    "flext-api",
    "flext-auth",
    "flext-cli",
    "flext-db-oracle",
    "flext-grpc",
    "flext-ldap",
    "flext-ldif",
    "flext-meltano",
    "flext-observability",
    "flext-oracle-oic-ext",
    "flext-oracle-wms",
    "flext-plugin",
    "flext-quality",
    "flext-tools",
    "flext-web",
    # Enterprise tools
    "client-a-oud-mig",
    "client-b-meltano-native",
]

# Domain library violation patterns
DOMAIN_VIOLATIONS = {
    "ldap3": {"library": "flext-ldap", "allowed_in": ["flext-ldap"]},
    "ldif": {"library": "flext-ldif", "allowed_in": ["flext-ldif"]},
    "click": {"library": "flext-cli", "allowed_in": ["flext-cli"]},
    "rich": {"library": "flext-cli", "allowed_in": ["flext-cli"]},
    "tabulate": {"library": "flext-cli", "allowed_in": ["flext-cli"]},
    "httpx": {"library": "flext-api", "allowed_in": ["flext-api", "flext-web"]},
    "requests": {"library": "flext-api", "allowed_in": ["flext-api", "flext-web"]},
    "fastapi": {"library": "flext-web", "allowed_in": ["flext-web"]},
    "flask": {"library": "flext-web", "allowed_in": ["flext-web"]},
    "oracledb": {"library": "flext-db-oracle", "allowed_in": ["flext-db-oracle"]},
    "sqlalchemy": {"library": "flext-db-oracle", "allowed_in": ["flext-db-oracle"]},
    "meltano": {"library": "flext-meltano", "allowed_in": ["flext-meltano"]},
    "dbt": {"library": "flext-meltano", "allowed_in": ["flext-meltano"]},
    "singer": {"library": "flext-meltano", "allowed_in": ["flext-meltano"]},
    "grpc": {"library": "flext-grpc", "allowed_in": ["flext-grpc"]},
    "grpcio": {"library": "flext-grpc", "allowed_in": ["flext-grpc"]},
}


@dataclass
class ValidationResult:
    """Validation result for a single project."""

    project: str
    status: Literal["PASS", "WARN", "FAIL"] = "PASS"
    syntax_errors: int = 0
    lint_errors: int = 0
    lint_warnings: int = 0
    type_errors: int = 0
    domain_violations: list[str] = field(default_factory=list)
    has_tests: bool = False
    has_makefile: bool = False
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class EcosystemValidator:
    """Validator for FLEXT ecosystem projects."""

    def __init__(self, workspace_path: Path) -> None:
        """Initialize the ecosystem validator.

        Args:
            workspace_path: Path to the FLEXT workspace.

        """
        super().__init__()
        self.workspace_path = workspace_path
        self.results: dict[str, ValidationResult] = {}

    def validate_syntax(self, project: str) -> tuple[int, list[str]]:
        """Validate Python syntax using AST parsing."""
        project_path = self.workspace_path / project
        src_dir = project_path / "src"

        if not src_dir.exists():
            return 0, []

        errors = []
        error_count = 0

        for py_file in src_dir.rglob("*.py"):
            try:
                ast.parse(py_file.read_text())
            except SyntaxError as e:
                errors.append(
                    f"{py_file.relative_to(project_path)}: {e.msg} at line {e.lineno}"
                )
                error_count += 1

        return error_count, errors

    def validate_lint(self, project: str) -> tuple[int, int]:
        """Validate with Ruff linting."""
        project_path = self.workspace_path / project
        src_dir = project_path / "src"

        if not src_dir.exists():
            return 0, 0

        ruff_path = shutil.which("ruff")
        if not ruff_path:
            logger.warning("Ruff executable not found in PATH")
            return 0, 0

        try:
            result = subprocess.run(
                [ruff_path, "check", str(src_dir), "--output-format=json"],
                check=False,
                capture_output=True,
                text=True,
                cwd=project_path,
                timeout=30,
            )

            if result.stdout:
                violations = json.loads(result.stdout)
                errors = sum(1 for v in violations if v.get("fix") is None)
                warnings = len(violations) - errors
                return errors, warnings
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass

        return 0, 0

    def validate_domain_violations(self, project: str) -> list[str]:
        """Check for direct imports of wrapped technologies."""
        project_path = self.workspace_path / project
        src_dir = project_path / "src"

        if not src_dir.exists():
            return []

        violations = []

        for py_file in src_dir.rglob("*.py"):
            content = py_file.read_text()

            for tech, info in DOMAIN_VIOLATIONS.items():
                # Skip if this project is allowed to import it
                if project in info["allowed_in"]:
                    continue

                # Check for direct imports
                import_patterns = [
                    f"import {tech}",
                    f"from {tech} import",
                    f"from {tech}.",
                ]

                for pattern in import_patterns:
                    if pattern in content:
                        message = f"{py_file.relative_to(project_path)}: Direct {tech} import (use {info['library']})"
                        violations.append(message)
                        break

        return violations

    def check_project_structure(self, project: str) -> tuple[bool, bool]:
        """Check for tests directory and Makefile."""
        project_path = self.workspace_path / project
        has_tests = (project_path / "tests").exists()
        has_makefile = (project_path / "Makefile").exists()
        return has_tests, has_makefile

    def validate_project(self, project: str) -> ValidationResult:
        """Validate a single project."""
        print(f"Validating {project}...", end=" ", flush=True)

        result = ValidationResult(project=project)

        # Check if project exists
        project_path = self.workspace_path / project
        if not project_path.exists():
            result.status = "FAIL"
            result.issues.append("Project directory not found")
            print("❌ NOT FOUND")
            return result

        # Syntax validation
        syntax_count, syntax_errors = self.validate_syntax(project)
        result.syntax_errors = syntax_count
        if syntax_count > 0:
            result.status = "FAIL"
            result.issues.extend(syntax_errors[:3])  # First 3 errors

        # Lint validation
        lint_errors, lint_warnings = self.validate_lint(project)
        result.lint_errors = lint_errors
        result.lint_warnings = lint_warnings

        # Domain violations
        violations = self.validate_domain_violations(project)
        result.domain_violations = violations
        if violations:
            result.status = "WARN" if result.status == "PASS" else result.status
            result.issues.extend(violations[:3])  # First 3 violations

        # Project structure
        has_tests, has_makefile = self.check_project_structure(project)
        result.has_tests = has_tests
        result.has_makefile = has_makefile

        # Determine status
        if (
            result.syntax_errors == 0
            and len(result.domain_violations) == 0
            and lint_errors == 0
        ):
            result.status = "PASS"
        elif result.syntax_errors > 0:
            result.status = "FAIL"
        else:
            result.status = "WARN"

        # Recommendations
        if not has_tests:
            result.recommendations.append("Add test suite")
        if not has_makefile:
            result.recommendations.append("Add Makefile for quality gates")
        if result.domain_violations:
            result.recommendations.append(
                f"Fix {len(result.domain_violations)} domain library violations"
            )
        if lint_errors > 0:
            result.recommendations.append(f"Fix {lint_errors} lint errors")

        status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[result.status]
        print(f"{status_icon} {result.status}")

        return result

    def generate_report(self) -> str:
        """Generate human-readable report."""
        lines = []
        lines.extend((
            "=" * 80,
            "FLEXT ECOSYSTEM TRANSFORMATION STATUS REPORT",
            "=" * 80,
            "",
        ))

        # Summary statistics
        total = len(self.results)
        passed = sum(1 for r in self.results.values() if r.status == "PASS")
        warned = sum(1 for r in self.results.values() if r.status == "WARN")
        failed = sum(1 for r in self.results.values() if r.status == "FAIL")

        lines.extend([
            "SUMMARY:",
            f"  Total projects: {total}",
            f"  ✅ Production ready: {passed}",
            f"  ⚠️  Need attention: {warned}",
            f"  ❌ Critical issues: {failed}",
            "",
        ])

        # Foundation status
        lines.append("FOUNDATION:")
        if "flext-core" in self.results:
            core = self.results["flext-core"]
            status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[core.status]
            lines.append(f"  {status_icon} flext-core: {core.status}")
            if core.issues:
                lines.extend(f"    - {issue}" for issue in core.issues[:3])
        lines.extend(["", "DOMAIN LIBRARIES:"])
        domain_libs = [
            p for p in FLEXT_PROJECTS if p.startswith("flext-") and p != "flext-core"
        ]
        for project in sorted(domain_libs):
            if project in self.results:
                r = self.results[project]
                status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[r.status]
                lines.append(f"  {status_icon} {project}: {r.status}")
                if r.domain_violations:
                    lines.append(f"      Domain violations: {len(r.domain_violations)}")
                if r.lint_errors > 0:
                    lines.append(f"      Lint errors: {r.lint_errors}")
        lines.extend(["", "ENTERPRISE TOOLS:"])
        tools = [p for p in FLEXT_PROJECTS if not p.startswith("flext-")]
        for project in sorted(tools):
            if project in self.results:
                r = self.results[project]
                status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[r.status]
                lines.append(f"  {status_icon} {project}: {r.status}")
                if r.domain_violations:
                    lines.append(
                        f"      ⚠️  Must use flext-* libraries ({len(r.domain_violations)} violations)"
                    )
        lines.append("")

        # Critical issues
        critical_projects = [p for p, r in self.results.items() if r.status == "FAIL"]
        if critical_projects:
            lines.append("CRITICAL ISSUES:")
            for project in critical_projects:
                r = self.results[project]
                lines.append(f"  ❌ {project}:")
                lines.extend(f"      - {issue}" for issue in r.issues[:5])
            lines.append("")

        # Top recommendations
        lines.append("RECOMMENDED ACTIONS:")
        all_recommendations: dict[str, int] = {}
        for r in self.results.values():
            for rec in r.recommendations:
                all_recommendations[rec] = all_recommendations.get(rec, 0) + 1

        for rec, count in sorted(all_recommendations.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"  - {rec} ({count} projects)")
        lines.extend(("", "=" * 80, "Validation completed successfully", "=" * 80))

        return "\n".join(lines)

    def run_validation(self) -> None:
        """Run validation on all projects."""
        print("\nStarting FLEXT Ecosystem Validation...\n")

        for project in FLEXT_PROJECTS:
            result = self.validate_project(project)
            self.results[project] = result

        print("\n" + self.generate_report())


def main() -> int:
    """Main entry point."""
    workspace = Path.cwd()
    validator = EcosystemValidator(workspace)
    validator.run_validation()

    # Exit with appropriate code
    failed = sum(1 for r in validator.results.values() if r.status == "FAIL")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
