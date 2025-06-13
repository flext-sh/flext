#!/usr/bin/env python3
"""Standardization Validator - Checks if all projects follow the standards."""

import sys
from pathlib import Path

import tomli
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def check_project_standards(project_path: Path) -> dict:
    """Check if a project follows the defined standards."""
    issues = []
    config_path = project_path / "pyproject.toml"

    if not config_path.exists():
        return {"issues": ["pyproject.toml not found"]}

    try:
        with open(config_path, "rb") as f:
            config = tomli.load(f)
    except Exception as e:
        return {"issues": [f"Error reading pyproject.toml: {e}"]}

    # Check build-system
    build_system = config.get("build-system", {})
    if "poetry-core" not in str(build_system.get("requires", [])):
        issues.append("build-system does not use poetry-core")

    # Check Python version
    tool_poetry = config.get("tool", {}).get("poetry", {})
    python_version = tool_poetry.get("dependencies", {}).get("python", "")
    if not python_version.startswith("^3.13"):
        issues.append(f"Incorrect Python version: {python_version}")

    # Check quality tools
    tool_config = config.get("tool", {})

    required_tools = ["black", "ruff", "mypy", "pytest.ini_options"]
    for tool in required_tools:
        if tool not in tool_config:
            issues.append(f"Missing tool: {tool}")

    # Check ruff target-version
    ruff_config = tool_config.get("ruff", {})
    if ruff_config.get("target-version") != "py312":
        issues.append(
            f"Incorrect Ruff target-version: {ruff_config.get('target-version')}",
        )

    # Check mypy python_version
    mypy_config = tool_config.get("mypy", {})
    if mypy_config.get("python_version") != "3.13":
        issues.append(
            f"Incorrect MyPy python_version: {mypy_config.get('python_version')}",
        )

    return {"issues": issues}


def main() -> None:
    """Main function."""
    workspace_path = Path.cwd()

    console.print(
        Panel.fit(
            "PYAUTO Standardization Validator\n"
            "Checks compliance with PEP8 & Poetry standards",
            style="bold blue",
        ),
    )

    # Find projects
    projects = []
    seen_projects = set()
    for path in workspace_path.rglob("pyproject.toml"):
        if any(
            part.startswith(".")
            and part
            in {".venv", ".mypy_cache", ".pytest_cache", ".standardization_backup"}
            for part in path.parts
        ):
            continue

        # Avoid duplicates based on project name
        project_path = path.parent
        if project_path.name not in seen_projects:
            projects.append(project_path)
            seen_projects.add(project_path.name)

    # Check each project
    table = Table(title="Standardization Status")
    table.add_column("Project", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Issues", style="red")

    total_issues = 0

    for project_path in projects:
        result = check_project_standards(project_path)
        issues = result["issues"]

        if issues:
            status = "❌ Non-Compliant"
            issues_text = "\n".join(issues[:3])  # Limit to 3 issues
            if len(issues) > 3:
                issues_text += f"\n... and {len(issues) - 3} more"
            total_issues += len(issues)
        else:
            status = "✅ Compliant"
            issues_text = "-"

        table.add_row(project_path.name, status, issues_text)

    console.print(table)

    if total_issues > 0:
        console.print(f"\n[red]Total issues found: {total_issues}[/red]")
        console.print(
            "[yellow]Run 'python standardize_projects.py' to fix[/yellow]",
        )
        sys.exit(1)
    else:
        console.print("\n[green]✅ All projects are compliant![/green]")


if __name__ == "__main__":
    main()
