#!/usr/bin/env python3
"""MyPy Error Analysis Script for FLEXT Projects
Analyzes MyPy errors across all flext-* projects systematically.
"""

import json
import os
import subprocess
from pathlib import Path


def get_project_directories() -> list[Path]:
    """Get all flext-* project directories."""
    base_path = Path("/home/marlonsc/flext")
    projects = []

    # Add main workspace
    if (base_path / "pyproject.toml").exists():
        projects.append(base_path)

    # Add all flext-* subdirectories with pyproject.toml
    for item in base_path.iterdir():
        if item.is_dir() and item.name.startswith("flext-"):
            if (item / "pyproject.toml").exists():
                projects.append(item)

    return sorted(projects)


def find_source_directory(project_path: Path) -> Path:
    """Find the source directory for a project (src/ or project_name/)."""
    # Check common source directory patterns
    candidates = [
        project_path / "src",
        project_path / project_path.name.replace("-", "_"),
        project_path / "flext",  # For main workspace
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            # Check if it has Python files
            if any(candidate.rglob("*.py")):
                return candidate

    return None


def run_mypy_analysis(project_path: Path) -> tuple[int, list[str], str]:
    """Run MyPy on a project and return error count, error lines, and categorized errors."""
    src_dir = find_source_directory(project_path)

    if not src_dir:
        return 0, [], "No source directory found"

    try:
        # Change to project directory
        original_cwd = Path.cwd()
        os.chdir(project_path)

        # Run MyPy
        result = subprocess.run(
            ["mypy", str(src_dir), "--show-error-codes", "--no-error-summary"],
            check=False, capture_output=True,
            text=True,
            timeout=60,
        )

        error_lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        error_count = len([line for line in error_lines if line.strip() and not line.startswith("Found")])

        return error_count, error_lines, f"Success - analyzed {src_dir.name}"

    except subprocess.TimeoutExpired:
        return -1, [], "Timeout"
    except FileNotFoundError:
        return -1, [], "MyPy not found"
    except Exception as e:
        return -1, [], f"Error: {e!s}"
    finally:
        os.chdir(original_cwd)


def categorize_errors(error_lines: list[str]) -> dict[str, int]:
    """Categorize MyPy errors by type."""
    categories = {
        "import-untyped": 0,
        "no-untyped-def": 0,
        "no-untyped-call": 0,
        "type-arg": 0,
        "attr-defined": 0,
        "arg-type": 0,
        "return-value": 0,
        "assignment": 0,
        "union-attr": 0,
        "misc-other": 0,
    }

    for line in error_lines:
        if not line.strip() or line.startswith("Found"):
            continue

        # Extract error code from [error-code] pattern
        if "[" in line and "]" in line:
            error_code = line.split("[")[-1].split("]")[0]
            if error_code in categories:
                categories[error_code] += 1
            else:
                categories["misc-other"] += 1
        else:
            categories["misc-other"] += 1

    return categories


def determine_priority(project_name: str, error_count: int) -> int:
    """Determine priority ranking (1=highest priority)."""
    # Critical foundation projects
    critical_projects = ["flext-core", "flext", "src"]
    if any(proj in project_name.lower() for proj in critical_projects):
        return 1

    # API and Authentication projects
    api_projects = ["flext-api", "flext-auth", "flext-cli"]
    if any(proj in project_name.lower() for proj in api_projects):
        return 2

    # Database and infrastructure projects
    infra_projects = ["flext-db-oracle", "flext-ldap", "flext-meltano", "flext-observability"]
    if any(proj in project_name.lower() for proj in infra_projects):
        return 3

    # Singer ecosystem projects
    singer_projects = ["flext-tap-", "flext-target-", "flext-dbt-"]
    if any(proj in project_name.lower() for proj in singer_projects):
        return 4

    # Other projects
    return 5


def main() -> None:
    """Main analysis function."""
    projects = get_project_directories()
    results = []

    for project_path in projects:
        project_name = project_path.name if project_path.name != "flext" else "flext-main-workspace"

        error_count, error_lines, status = run_mypy_analysis(project_path)

        if error_count >= 0:
            categories = categorize_errors(error_lines)
            priority = determine_priority(project_name, error_count)

            results.append({
                "project": project_name,
                "path": str(project_path),
                "error_count": error_count,
                "categories": categories,
                "priority": priority,
                "status": status,
            })

    # Sort by priority, then by error count
    results.sort(key=lambda x: (x["priority"], -x["error_count"]))

    top_errors = sorted(results, key=lambda x: -x["error_count"])[:5]
    for result in top_errors:
        pass

    for result in results:
        if result["error_count"] > 0:
            ["🔴", "🟠", "🟡", "🔵", "⚪"][min(result["priority"] - 1, 4)]

    total_categories = {}
    for result in results:
        for category, count in result["categories"].items():
            total_categories[category] = total_categories.get(category, 0) + count

    for category, count in sorted(total_categories.items(), key=lambda x: -x[1]):
        if count > 0:
            pass

    # Save detailed results
    with open("mypy_analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
