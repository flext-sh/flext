#!/usr/bin/env python
"""Zero Tolerance Validator - Quick validation of PEP8 compliance."""

import subprocess
import sys
from pathlib import Path


def validate_project(project_name: str) -> tuple[int, int, int]:
    """Validate a single project for zero tolerance compliance."""
    project_path = Path(f"/home/marlonsc/pyauto/{project_name}")

    if not project_path.exists():
        return -1, -1, -1

    # Count ruff violations
    ruff_result = subprocess.run(
        ["poetry", "run", "ruff", "check", ".", "--quiet"],
        cwd=project_path,
        capture_output=True,
        text=True,
        check=False,
    )
    ruff_violations = len([l for l in ruff_result.stdout.split("\n") if l.strip()])

    # Check mypy
    mypy_result = subprocess.run(
        ["poetry", "run", "mypy", ".", "--no-error-summary"],
        cwd=project_path,
        capture_output=True,
        text=True,
        check=False,
    )
    mypy_errors = 1 if mypy_result.returncode != 0 else 0

    # Check tests
    test_result = subprocess.run(
        ["poetry", "run", "pytest", "--tb=no", "-q"],
        cwd=project_path,
        capture_output=True,
        text=True,
        check=False,
    )
    test_failures = 1 if test_result.returncode != 0 else 0

    return ruff_violations, mypy_errors, test_failures


def main() -> None:
    """Main validation function."""
    submodules = [
        "client-a-oud-mig",
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
        "client-b-poc-oic-wms",
        "ldap-core-shared",
        "oracle-oic-ext",
        "tap-ldap",
        "tap-oracle-oic",
        "tap-oracle-wms",
        "target-ldap",
        "target-oracle-oic",
        "target-oracle-wms",
    ]

    total_ruff = 0
    total_mypy = 0
    total_tests = 0
    compliant_projects = 0

    for project in submodules:
        ruff, mypy, tests = validate_project(project)

        if ruff == -1:
            continue

        total_ruff += ruff
        total_mypy += mypy
        total_tests += tests

        status = (
            "✅ COMPLIANT" if (ruff == 0 and mypy == 0 and tests == 0) else "❌ FAILED"
        )
        if status == "✅ COMPLIANT":
            compliant_projects += 1

    if total_ruff + total_mypy + total_tests > 0:
        sys.exit(1)
        sys.exit(0)


if __name__ == "__main__":
    main()
