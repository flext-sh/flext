#!/usr/bin/env python3
"""
Comprehensive validation script for all LDAP projects.

This script validates that all projects follow strict PEP8 compliance,
have proper Poetry configuration, and are ready for Python 3.9+ compatibility.

Usage:
    python scripts/validate_all_projects.py
    python scripts/validate_all_projects.py --fix
    python scripts/validate_all_projects.py --project tap-ldap
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

PROJECTS = {
    "tap-ldap": {
        "type": "singer_tap",
        "python_range": "^3.9",
        "has_tests": True,
        "has_src": True,
    },
    "target-ldap": {
        "type": "singer_target",
        "python_range": "^3.9",
        "has_tests": True,
        "has_src": True,
    },
    "dbt-ldap": {
        "type": "dbt_project",
        "python_range": "^3.9",
        "has_tests": True,
        "has_src": False,
    },
    "flx-ldap": {
        "type": "orchestrator",
        "python_range": "^3.9",
        "has_tests": True,
        "has_src": True,
    },
}


def run_command(
    cmd: list[str], cwd: Path | None = None, check: bool = True
) -> subprocess.CompletedProcess:
    """Run command and return result."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        check=check,
    )


def validate_poetry_config(project_path: Path) -> dict[str, Any]:
    """Validate Poetry configuration."""
    results = {
        "pyproject_exists": False,
        "poetry_check": False,
        "python_version": None,
        "has_dev_deps": False,
        "has_security_tools": False,
        "errors": [],
    }

    pyproject_file = project_path / "pyproject.toml"
    results["pyproject_exists"] = pyproject_file.exists()

    if not results["pyproject_exists"]:
        results["errors"].append("pyproject.toml not found")
        return results

    try:
        # Check Poetry configuration
        result = run_command(["poetry", "check"],
                             cwd=project_path, check=False)
        results["poetry_check"] = result.returncode == 0
        if result.returncode != 0:
            results["errors"].append(f"Poetry check failed: {result.stderr}")

        # Parse pyproject.toml for details
        import tomllib

        with open(pyproject_file, "rb") as f:
            config = tomllib.load(f)

        # Check Python version
        python_version = (
            config.get("tool", {})
            .get("poetry", {})
            .get("dependencies", {})
            .get("python")
        )
        results["python_version"] = python_version

        if python_version != "^3.9":
            results["errors"].append(
                f"Python version should be ^3.9, got {python_version}"
            )

        # Check dev dependencies
        dev_deps = (
            config.get("tool", {})
            .get("poetry", {})
            .get("group", {})
            .get("dev", {})
            .get("dependencies", {})
        )
        results["has_dev_deps"] = len(dev_deps) > 0

        # Check for security tools
        security_tools = {"bandit", "safety", "pre-commit"}
        found_tools = security_tools.intersection(dev_deps.keys())
        results["has_security_tools"] = len(found_tools) >= 2

        if not results["has_security_tools"]:
            results["errors"].append(
                f"Missing security tools. Found: {found_tools}, Expected: {security_tools}")

    except Exception as e:
        results["errors"].append(f"Error parsing pyproject.toml: {e}")

    return results


def validate_code_quality(
    project_path: Path, project_info: dict[str, Any], fix: bool = False
) -> dict[str, Any]:
    """Validate code quality with linting and formatting."""
    results = {
        "format_check": False,
        "lint_check": False,
        "type_check": False,
        "security_check": False,
        "errors": [],
    }

    try:
        # Check if poetry is installed
        poetry_result = run_command(
            ["poetry", "--version"], cwd=project_path, check=False
        )
        if poetry_result.returncode != 0:
            results["errors"].append("Poetry not available")
            return results

        # Install dependencies first
        install_result = run_command(
            ["poetry", "install", "--with", "dev"], cwd=project_path, check=False
        )
        if install_result.returncode != 0:
            results["errors"].append(
                f"Poetry install failed: {
                    install_result.stderr}")
            return results

        # Format check/fix
        if fix:
            format_result = run_command(
                ["poetry", "run", "ruff", "format", "."], cwd=project_path, check=False
            )
            format_result = run_command(
                ["poetry", "run", "ruff", "format", "--check", "."],
                cwd=project_path,
                check=False,
            )

        results["format_check"] = format_result.returncode == 0
        if format_result.returncode != 0:
            results["errors"].append(
                f"Format check failed: {
                    format_result.stdout}")

        # Linting
        lint_args = ["poetry", "run", "ruff", "check"]
        if fix:
            lint_args.append("--fix")
        lint_args.append(".")

        lint_result = run_command(lint_args, cwd=project_path, check=False)
        results["lint_check"] = lint_result.returncode == 0
        if lint_result.returncode != 0:
            results["errors"].append(
                f"Lint check failed: {
                    lint_result.stdout}")

        # Type checking (only for projects with src/)
        if project_info.get("has_src"):
            type_result = run_command(
                ["poetry", "run", "mypy", "src/"], cwd=project_path, check=False
            )
            results["type_check"] = type_result.returncode == 0
            if type_result.returncode != 0:
                results["errors"].append(
                    f"Type check failed: {
                        type_result.stdout}")
            results["type_check"] = True  # Skip for dbt projects

        # Security check
        security_result = run_command(
            ["poetry", "run", "bandit", "-r", ".", "-f", "json"],
            cwd=project_path,
            check=False,
        )
        results["security_check"] = security_result.returncode == 0
        if security_result.returncode not in {
                0, 1}:  # 1 is issues found, which is ok
            results["errors"].append(
                f"Security check failed: {
                    security_result.stderr}")

    except Exception as e:
        results["errors"].append(f"Error during code quality checks: {e}")

    return results


def validate_structure(
    project_path: Path, project_info: dict[str, Any]
) -> dict[str, Any]:
    """Validate project structure."""
    results = {
        "has_readme": False,
        "has_gitignore": False,
        "has_makefile": False,
        "has_github_workflows": False,
        "has_precommit": False,
        "has_tests": False,
        "errors": [],
    }

    # Required files
    required_files = {
        "README.md": "has_readme",
        ".gitignore": "has_gitignore",
        "Makefile": "has_makefile",
        ".pre-commit-config.yaml": "has_precommit",
    }

    for file_name, result_key in required_files.items():
        file_path = project_path / file_name
        results[result_key] = file_path.exists()
        if not results[result_key]:
            results["errors"].append(f"Missing {file_name}")

    # GitHub workflows
    workflows_dir = project_path / ".github" / "workflows"
    results["has_github_workflows"] = workflows_dir.exists() and any(
        workflows_dir.glob("*.yml")
    )
    if not results["has_github_workflows"]:
        results["errors"].append("Missing GitHub workflows")

    # Tests directory
    tests_dir = project_path / "tests"
    if project_info.get("has_tests", True):
        results["has_tests"] = tests_dir.exists()
        if not results["has_tests"]:
            results["errors"].append("Missing tests directory")
        results["has_tests"] = True

    return results


@click.command()
@click.option("--project", help="Specific project to validate")
@click.option("--fix", is_flag=True,
              help="Attempt to fix issues automatically")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def main(project: str | None, fix: bool, verbose: bool) -> None:
    """Validate all LDAP projects for PEP8 compliance and Python 3.9+ compatibility."""

    console.print(Panel.fit("🔍 LDAP Projects Validation", style="bold blue"))

    pyauto_root = Path(__file__).parent.parent
    projects_to_check = [project] if project else list(PROJECTS.keys())

    overall_results: dict = {}

    for project_name in projects_to_check:
        if project_name not in PROJECTS:
            console.print(f"❌ Unknown project: {project_name}")
            continue

        project_path = pyauto_root / project_name
        project_info = PROJECTS[project_name]

        console.print(
            f"\n📁 Validating {project_name} ({
                project_info['type']})...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Poetry validation
            task1 = progress.add_task(
                "Checking Poetry configuration...", total=None)
            poetry_results = validate_poetry_config(project_path)
            progress.update(task1, completed=True)

            # Structure validation
            task2 = progress.add_task(
                "Checking project structure...", total=None)
            structure_results = validate_structure(project_path, project_info)
            progress.update(task2, completed=True)

            # Code quality validation
            task3 = progress.add_task("Checking code quality...", total=None)
            quality_results = validate_code_quality(
                project_path, project_info, fix)
            progress.update(task3, completed=True)

        overall_results[project_name] = {
            "poetry": poetry_results,
            "structure": structure_results,
            "quality": quality_results,
        }

    # Display results
    console.print("\n📊 Validation Results")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Project", style="cyan")
    table.add_column("Poetry", justify="center")
    table.add_column("Structure", justify="center")
    table.add_column("Code Quality", justify="center")
    table.add_column("Python 3.9+", justify="center")
    table.add_column("Issues", justify="center")

    for project_name, results in overall_results.items():
        poetry = results["poetry"]
        structure = results["structure"]
        quality = results["quality"]

        # Poetry status
        poetry_status = (
            "✅"
            if poetry["poetry_check"] and poetry["python_version"] == "^3.9"
            else "❌"
        )

        # Structure status
        structure_checks = [
            structure["has_readme"],
            structure["has_gitignore"],
            structure["has_makefile"],
            structure["has_github_workflows"],
            structure["has_precommit"],
            structure["has_tests"],
        ]
        structure_status = "✅" if all(structure_checks) else "❌"

        # Quality status
        quality_checks = [
            quality["format_check"],
            quality["lint_check"],
            quality["type_check"],
            quality["security_check"],
        ]
        quality_status = "✅" if all(quality_checks) else "❌"

        # Python 3.9+ compatibility
        python_status = "✅" if poetry["python_version"] == "^3.9" else "❌"

        # Count issues
        total_issues = (len(poetry["errors"]) +
                        len(structure["errors"]) +
                        len(quality["errors"]))
        issues_status = "✅" if total_issues == 0 else f"❌ ({total_issues})"

        table.add_row(
            project_name,
            poetry_status,
            structure_status,
            quality_status,
            python_status,
            issues_status,
        )

    console.print(table)

    # Detailed error reporting
    if verbose:
        for project_name, results in overall_results.items():
            all_errors = (
                results["poetry"]["errors"]
                + results["structure"]["errors"]
                + results["quality"]["errors"]
            )

            if all_errors:
                console.print(f"\n❌ Issues in {project_name}:")
                for error in all_errors:
                    console.print(f"  • {error}")

    # Summary
    total_projects = len(overall_results)
    valid_projects = sum(
        1
        for results in overall_results.values()
        if len(results["poetry"]["errors"]) == 0
        and len(results["structure"]["errors"]) == 0
        and len(results["quality"]["errors"]) == 0
        and results["poetry"]["python_version"] == "^3.9"
    )

    action_text = "Fixed and validated" if fix else "Validated"
    console.print(
        f"\n🎯 Summary: {action_text} {valid_projects}/{total_projects} projects for Python 3.9+ compatibility and strict PEP8 compliance"
    )

    if valid_projects == total_projects:
        console.print("✅ All projects are ready for production!")
        sys.exit(0)
        console.print("❌ Some projects need attention.")
        if not fix:
            console.print("💡 Run with --fix to attempt automatic fixes.")
        sys.exit(1)


if __name__ == "__main__":
    main()
