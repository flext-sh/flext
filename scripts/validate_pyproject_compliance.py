#!/usr/bin/env python3
"""
PyProject Template Compliance Validator

Validates that all PyAuto projects conform to the enterprise pyproject.toml template.
ZERO TOLERANCE enforcement for deviations from standards.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()

# Enterprise standards - ZERO TOLERANCE
REQUIRED_PYTHON_VERSION = ">=3.9,<4.0"
REQUIRED_BUILD_SYSTEM = "poetry-core>=1.9.0"
MINIMUM_COVERAGE = 90
REQUIRED_LINE_LENGTH = 88

# Required development dependencies (minimum versions)
REQUIRED_DEV_DEPS = {
    "pytest": "^8.3.4",
    "pytest-cov": "^6.0.0",
    "black": "^24.10.0",
    "ruff": "^0.8.3",
    "mypy": "^1.13.0",
    "bandit": "^1.8.0",
}

# Required core dependencies
REQUIRED_CORE_DEPS = {
    "pydantic": "^2.11.0",
    "structlog": "^24.4.0",
    "python-dotenv": "^1.0.1",
    "typing-extensions": "^4.12.2",
}

# Critical tool configurations
REQUIRED_BLACK_CONFIG = {
    "line-length": 88,
    "target-version": ["py39", "py310", "py311", "py312", "py313"],
}

REQUIRED_RUFF_CONFIG = {
    "line-length": 88,
    "target-version": "py39",
}

REQUIRED_MYPY_CONFIG = {
    "python_version": "3.9",
    "strict": True,
    "warn_return_any": True,
    "disallow_untyped_defs": True,
}

REQUIRED_PYTEST_CONFIG = {
    "cov-fail-under": "90",
    "strict-markers": True,
    "strict-config": True,
}


class ComplianceError(Exception):
    """Raised when a project fails compliance validation."""


def load_pyproject(project_path: Path) -> dict[str, Any]:
    """Load and parse pyproject.toml file."""
    pyproject_file = project_path / "pyproject.toml"
    if not pyproject_file.exists():
        raise ComplianceError(f"Missing pyproject.toml in {project_path}")

    try:
        with open(pyproject_file, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        raise ComplianceError(f"Invalid pyproject.toml in {project_path}: {e}")


def validate_build_system(config: dict[str, Any], project_name: str) -> list[str]:
    """Validate build system configuration."""
    violations = []
    build_system = config.get("build-system", {})

    requires = build_system.get("requires", [])
    if not any(req.startswith("poetry-core") for req in requires):
        violations.append("Missing poetry-core in build-system.requires")

    backend = build_system.get("build-backend")
    if backend != "poetry.core.masonry.api":
        violations.append(f"Invalid build-backend: {backend}")

    return violations


def validate_python_version(config: dict[str, Any], project_name: str) -> list[str]:
    """Validate Python version requirement."""
    violations = []
    poetry_config = config.get("tool", {}).get("poetry", {})
    dependencies = poetry_config.get("dependencies", {})
    python_version = dependencies.get("python")

    if python_version != REQUIRED_PYTHON_VERSION:
        violations.append(
            f"Invalid Python version: {python_version}, required: {REQUIRED_PYTHON_VERSION}"
        )

    return violations


def validate_core_dependencies(config: dict[str, Any], project_name: str) -> list[str]:
    """Validate core production dependencies."""
    violations = []
    poetry_config = config.get("tool", {}).get("poetry", {})
    dependencies = poetry_config.get("dependencies", {})

    for dep_name, _required_version in REQUIRED_CORE_DEPS.items():
        actual_version = dependencies.get(dep_name)
        if not actual_version:
            violations.append(f"Missing required dependency: {dep_name}")
        elif not actual_version.startswith("^"):
            violations.append(
                f"Invalid version format for {dep_name}: {actual_version} (use caret)"
            )

    return violations


def validate_dev_dependencies(config: dict[str, Any], project_name: str) -> list[str]:
    """Validate development dependencies."""
    violations = []
    poetry_config = config.get("tool", {}).get("poetry", {})
    dev_deps = poetry_config.get("group", {}).get("dev", {}).get("dependencies", {})

    for dep_name, _required_version in REQUIRED_DEV_DEPS.items():
        actual_version = dev_deps.get(dep_name)
        if not actual_version:
            violations.append(f"Missing required dev dependency: {dep_name}")

    return violations


def validate_black_config(config: dict[str, Any], project_name: str) -> list[str]:
    """Validate Black configuration."""
    violations = []
    black_config = config.get("tool", {}).get("black", {})

    for key, required_value in REQUIRED_BLACK_CONFIG.items():
        actual_value = black_config.get(key)
        if actual_value != required_value:
            violations.append(
                f"Invalid Black {key}: {actual_value}, required: {required_value}"
            )

    return violations


def validate_ruff_config(config: dict[str, Any], project_name: str) -> list[str]:
    """Validate Ruff configuration."""
    violations = []
    ruff_config = config.get("tool", {}).get("ruff", {})

    for key, required_value in REQUIRED_RUFF_CONFIG.items():
        actual_value = ruff_config.get(key)
        if actual_value != required_value:
            violations.append(
                f"Invalid Ruff {key}: {actual_value}, required: {required_value}"
            )

    # Check that comprehensive rule selection is present
    lint_config = ruff_config.get("lint", {})
    select_rules = lint_config.get("select", [])

    # Minimum required rule categories
    required_rules = ["F", "E", "W", "I", "N", "D", "UP", "ANN", "B", "S"]
    missing_rules = [rule for rule in required_rules if rule not in select_rules]
    if missing_rules:
        violations.append(f"Missing required Ruff rules: {missing_rules}")

    return violations


def validate_mypy_config(config: dict[str, Any], project_name: str) -> list[str]:
    """Validate MyPy configuration."""
    violations = []
    mypy_config = config.get("tool", {}).get("mypy", {})

    for key, required_value in REQUIRED_MYPY_CONFIG.items():
        actual_value = mypy_config.get(key)
        if actual_value != required_value:
            violations.append(
                f"Invalid MyPy {key}: {actual_value}, required: {required_value}"
            )

    return violations


def validate_pytest_config(config: dict[str, Any], project_name: str) -> list[str]:
    """Validate Pytest configuration."""
    violations = []
    pytest_config = config.get("tool", {}).get("pytest", {}).get("ini_options", {})
    addopts = pytest_config.get("addopts", [])

    # Check for critical options
    required_opts = ["--cov-fail-under=90", "--strict-markers", "--strict-config"]
    for opt in required_opts:
        if opt not in addopts:
            violations.append(f"Missing required pytest option: {opt}")

    return violations


def validate_coverage_config(config: dict[str, Any], project_name: str) -> list[str]:
    """Validate coverage configuration."""
    violations = []
    coverage_config = config.get("tool", {}).get("coverage", {})
    report_config = coverage_config.get("report", {})

    fail_under = report_config.get("fail_under")
    if fail_under != MINIMUM_COVERAGE:
        violations.append(
            f"Invalid coverage fail_under: {fail_under}, required: {MINIMUM_COVERAGE}"
        )

    return violations


def validate_project_metadata(config: dict[str, Any], project_name: str) -> list[str]:
    """Validate project metadata completeness."""
    violations = []
    poetry_config = config.get("tool", {}).get("poetry", {})

    required_fields = ["name", "version", "description", "authors", "license"]
    for field in required_fields:
        if not poetry_config.get(field):
            violations.append(f"Missing required project metadata: {field}")

    # Validate classifiers presence
    classifiers = poetry_config.get("classifiers", [])
    if not classifiers:
        violations.append("Missing project classifiers")

    return violations


def validate_project(project_path: Path) -> tuple[str, list[str]]:
    """Validate a single project for template compliance."""
    project_name = project_path.name
    logger.info("Validating project", project=project_name)

    try:
        config = load_pyproject(project_path)
    except ComplianceError as e:
        return project_name, [str(e)]

    all_violations = []

    # Run all validation checks
    validators = [
        validate_build_system,
        validate_python_version,
        validate_core_dependencies,
        validate_dev_dependencies,
        validate_black_config,
        validate_ruff_config,
        validate_mypy_config,
        validate_pytest_config,
        validate_coverage_config,
        validate_project_metadata,
    ]

    for validator in validators:
        violations = validator(config, project_name)
        all_violations.extend(violations)

    return project_name, all_violations


def find_pyauto_projects(workspace_path: Path) -> list[Path]:
    """Find all PyAuto projects with pyproject.toml files."""
    projects = []

    # Look for directories with pyproject.toml files
    for item in workspace_path.iterdir():
        if item.is_dir() and (item / "pyproject.toml").exists():
            # Skip template and root project
            if item.name not in ["pyproject-template.toml", "."]:
                projects.append(item)

    return sorted(projects)


def main() -> int:
    """Main validation entry point."""
    logger.info("Starting PyProject Template Compliance Validation")

    workspace_path = Path.cwd()
    projects = find_pyauto_projects(workspace_path)

    if not projects:
        logger.error("No PyAuto projects found with pyproject.toml files")
        return 1

    logger.info("Found projects for validation", count=len(projects))

    total_violations = 0
    failed_projects = []

    for project_path in projects:
        project_name, violations = validate_project(project_path)

        if violations:
            failed_projects.append(project_name)
            total_violations += len(violations)
            logger.error(
                "Project compliance violations",
                project=project_name,
                violations=violations,
                count=len(violations)
            )
        else:
            logger.info("Project compliant", project=project_name)

    # Summary report
    logger.info(
        "Validation complete",
        total_projects=len(projects),
        compliant_projects=len(projects) - len(failed_projects),
        failed_projects=len(failed_projects),
        total_violations=total_violations
    )

    if failed_projects:
        logger.error(
            "COMPLIANCE FAILURE - Projects require template application",
            failed_projects=failed_projects
        )
        print("\n" + "=" * 80)
        print("ENTERPRISE COMPLIANCE FAILURE")
        print("=" * 80)
        print(f"Failed Projects: {len(failed_projects)}/{len(projects)}")
        print(f"Total Violations: {total_violations}")
        print("\nFailed Projects:")
        for project in failed_projects:
            print(f"  - {project}")
        print("\nAction Required:")
        print("1. Apply pyproject-template.toml to all failed projects")
        print("2. Update project-specific dependencies")
        print("3. Re-run validation until ZERO violations")
        print("=" * 80)
        return 1

    logger.info("ALL PROJECTS COMPLIANT - Enterprise standards maintained")
    return 0


if __name__ == "__main__":
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    sys.exit(main())
