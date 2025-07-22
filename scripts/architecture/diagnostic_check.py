#!/usr/bin/env python3
"""Diagnóstico Completo do Workspace FLEXT.

Verifica lint, mypy, testes e violações arquiteturais em todos os submódulos
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ProjectStatus:
    """Project status."""

    name: str
    level: int
    has_makefile: bool
    has_pyproject: bool
    lint_status: str = "SKIP"
    mypy_status: str = "SKIP"
    test_status: str = "SKIP"
    poetry_install: str = "SKIP"
    errors: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        pass


class FlextDiagnostic:
    """Flext diagnostic tool."""

    def __init__(self, workspace_root: str = ".") -> None:
        self.workspace_root = Path(workspace_root).resolve()
        self.results: dict[str, ProjectStatus] = {}

        # Define layer hierarchy
        self.project_levels = {
            # LEVEL 1 - BASE
            "flext-core": 1,
            # LEVEL 2 - INTERMEDIATE
            "flext-cli": 2,
            "flext-observability": 2,
            "flext-grpc": 2,
            "flext-web": 2,
            "flext-api": 2,
            "flext-auth": 2,
            # LEVEL 3 - TECHNICAL BASES
            "flext-meltano": 3,
            "flext-ldif": 3,
            "flext-ldap": 3,
            "flext-db-oracle": 3,
            "flext-oracle-wms": 3,
            "flext-oracle-oic-ext": 3,
            # LEVEL 4 - MELTANO PLUGINS
            "flext-tap-oracle": 4,
            "flext-tap-ldap": 4,
            "flext-tap-ldif": 4,
            "flext-tap-oracle-wms": 4,
            "flext-tap-oracle-oic": 4,
            "flext-target-oracle": 4,
            "flext-target-ldap": 4,
            "flext-target-ldif": 4,
            "flext-target-oracle-wms": 4,
            "flext-target-oracle-oic": 4,
            "flext-dbt-oracle": 4,
            "flext-dbt-ldap": 4,
            "flext-dbt-ldif": 4,
            "flext-dbt-oracle-wms": 4,
            "flext-plugin": 4,
            # LEVEL 6 - SPECIFIC PROJECTS
            "client-a-oud-mig": 6,
            "client-b-meltano-native": 6,
        }

    def run_command(self, cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
        """Execute command and return (return_code, stdout, stderr)."""
        try:
            result = subprocess.run(cmd, check=False, cwd=cwd or self.workspace_root, capture_output=True, text=True, timeout=300)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout expired"
        except Exception as e:
            return -1, "", str(e)

    def check_project(self, project_name: str) -> ProjectStatus:
        """Check status of a project."""
        project_path = self.workspace_root / project_name

        if not project_path.exists():
            return ProjectStatus(
                name=project_name,
                level=self.project_levels.get(project_name, 0),
                has_makefile=False,
                has_pyproject=False,
                errors=["Project not found"],
            )

        status = ProjectStatus(
            name=project_name,
            level=self.project_levels.get(project_name, 0),
            has_makefile=(project_path / "Makefile").exists(),
            has_pyproject=(project_path / "pyproject.toml").exists(),
        )

        print(f"🔍 Checking {project_name} (Level {status.level})...")

        # Check Makefile
        if status.has_makefile:
            # Check lint
            rc, stdout, stderr = self.run_command(["make", "lint"], project_path)
            if rc == 0:
                status.lint_status = "✅ PASS"
            elif rc == 2:  # Makefile without lint target
                status.lint_status = "⚠️  NO_TARGET"
            else:
                status.lint_status = "❌ FAIL"
                status.errors.append(f"Lint: {stderr.strip()}")

            # Check mypy
            rc, stdout, stderr = self.run_command(["make", "mypy-check"], project_path)
            if rc == 0:
                status.mypy_status = "✅ PASS"
            elif rc == 2:  # Makefile without mypy-check target
                status.mypy_status = "⚠️  NO_TARGET"
            else:
                status.mypy_status = "❌ FAIL"
                status.errors.append(f"MyPy: {stderr.strip()}")

            # Check tests
            rc, stdout, stderr = self.run_command(["make", "test"], project_path)
            if rc == 0:
                status.test_status = "✅ PASS"
            elif rc == 2:  # Makefile without test target
                status.test_status = "⚠️  NO_TARGET"
            else:
                status.test_status = "❌ FAIL"
                status.errors.append(f"Tests: {stderr.strip()}")

        # Check Poetry install
        if status.has_pyproject:
            rc, stdout, stderr = self.run_command(["poetry", "install"], project_path)
            if rc == 0:
                status.poetry_install = "✅ PASS"
            else:
                status.poetry_install = "❌ FAIL"
                status.errors.append(f"Poetry: {stderr.strip()}")

        return status

    def check_architecture_violations(self) -> dict[str, list[str]]:
        """Check architecture violations."""
        violations: dict[str, list[str]] = {}

        # Check flext-core (should not have specific imports)
        core_path = self.workspace_root / "flext-core" / "src"
        if core_path.exists():
            violations["flext-core"] = []

            # Search problematic imports
            keywords = ["meltano", "oracle", "ldap", "singer", "client-a", "client-b"]
            for keyword in keywords:
                rc, stdout, stderr = self.run_command(["grep", "-r", keyword, "--include=*.py", "."], core_path)

                if rc == 0 and stdout.strip():
                    violations["flext-core"].append(f"Import {keyword}: {stdout.strip()}")

        return violations

    def run_full_diagnostic(self) -> dict[str, Any]:
        """Run full diagnostic."""
        print("🚀 INICIANDO DIAGNÓSTICO COMPLETO DO WORKSPACE FLEXT")
        print("=" * 60)

        # Check all projects
        for project_name in self.project_levels:
            status = self.check_project(project_name)
            self.results[project_name] = status

            # Check architecture violations
        violations = self.check_architecture_violations()

        # Generate report
        return {
            "timestamp": datetime.now().isoformat(),
            "workspace_root": str(self.workspace_root),
            "projects": {
                name: {
                    "level": status.level,
                    "has_makefile": status.has_makefile,
                    "has_pyproject": status.has_pyproject,
                    "lint_status": status.lint_status,
                    "mypy_status": status.mypy_status,
                    "test_status": status.test_status,
                    "poetry_install": status.poetry_install,
                    "errors": status.errors,
                }
                for name, status in self.results.items()
            },
            "architecture_violations": violations,
            "summary": self.generate_summary(),
        }

    def generate_summary(self) -> dict[str, Any]:
        """Generate summary."""
        total_projects = len(self.results)
        projects_with_makefile = sum(1 for s in self.results.values() if s.has_makefile)
        projects_with_pyproject = sum(1 for s in self.results.values() if s.has_pyproject)

        lint_passed = sum(1 for s in self.results.values() if s.lint_status == "✅ PASS")
        mypy_passed = sum(1 for s in self.results.values() if s.mypy_status == "✅ PASS")
        tests_passed = sum(1 for s in self.results.values() if s.test_status == "✅ PASS")
        poetry_passed = sum(1 for s in self.results.values() if s.poetry_install == "✅ PASS")

        projects_with_errors = sum(1 for s in self.results.values() if s.errors)

        return {
            "total_projects": total_projects,
            "projects_with_makefile": projects_with_makefile,
            "projects_with_pyproject": projects_with_pyproject,
            "lint_passed": lint_passed,
            "mypy_passed": mypy_passed,
            "tests_passed": tests_passed,
            "poetry_passed": poetry_passed,
            "projects_with_errors": projects_with_errors,
        }

    def print_report(self, report: dict) -> None:
        """Print formatted report."""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE DIAGNÓSTICO FLEXT")
        print("=" * 60)

        # Summary
        summary = report["summary"]
        print("\n📈 RESUMO GERAL:")
        print(f"   Total de projetos: {summary['total_projects']}")
        print(f"   Com Makefile: {summary['projects_with_makefile']}")
        print(f"   Com pyproject.toml: {summary['projects_with_pyproject']}")
        print(f"   Lint passou: {summary['lint_passed']}")
        print(f"   MyPy passou: {summary['mypy_passed']}")
        print(f"   Testes passaram: {summary['tests_passed']}")
        print(f"   Poetry install passou: {summary['poetry_passed']}")
        print(f"   Projetos com erros: {summary['projects_with_errors']}")

        # Project details
        print("\n🔍 DETALHES POR PROJETO:")
        print("-" * 60)

        for level in range(1, 7):
            level_projects = [(name, data) for name, data in report["projects"].items() if data["level"] == level]

            if level_projects:
                level_name = {
                    1: "NÍVEL 1 - BASE",
                    2: "NÍVEL 2 - INTERMEDIÁRIA",
                    3: "NÍVEL 3 - BASES TECNOLÓGICAS",
                    4: "NÍVEL 4 - PLUGINS MELTANO",
                    5: "NÍVEL 5 - WORKSPACE",
                    6: "NÍVEL 6 - PROJETOS ESPECÍFICOS",
                }.get(level, f"NÍVEL {level}")

                print(f"\n{level_name}:")
                for name, data in level_projects:
                    status_icons = [data["lint_status"], data["mypy_status"], data["test_status"], data["poetry_install"]]
                    status_str = " | ".join(status_icons)
                    print(f"  {name:<25} {status_str}")

                    if data["errors"]:
                        for error in data["errors"][:2]:  # Show only first 2 errors
                            print(f"    ❌ {error[:80]}...")

        # Architecture violations
        if report["architecture_violations"]:
            print("\n🚨 VIOLAÇÕES ARQUITETURAIS:")
            print("-" * 60)
            for project, violations in report["architecture_violations"].items():
                print(f"\n{project}:")
                for violation in violations:
                    print(f"  ❌ {violation}")

        print("\n" + "=" * 60)
        print("✅ DIAGNÓSTICO CONCLUÍDO")


def main() -> None:
    """Main function."""
    diagnostic = FlextDiagnostic()
    report = diagnostic.run_full_diagnostic()
    diagnostic.print_report(report)

    # Save report in JSON
    report_file = "scripts/architecture/diagnostic_report.json"
    os.makedirs(os.path.dirname(report_file), exist_ok=True)

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Relatório salvo em: {report_file}")

    # Return exit code based on errors
    if report["summary"]["projects_with_errors"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
