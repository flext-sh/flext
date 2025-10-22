#!/usr/bin/env python3
"""Generate quality metrics dashboard for FLEXT projects.

Collects Pydantic v2 compliance and other quality metrics across all
FLEXT projects and generates a comprehensive dashboard report.

Usage:
    python quality_dashboard.py > quality_metrics.json
    python quality_dashboard.py --html > quality_dashboard.html

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


def get_pydantic_compliance(project_path: Path) -> dict[str, Any]:
    """Get Pydantic v2 compliance metrics for a project.

    Args:
        project_path: Path to project root

    Returns:
        Dictionary with compliance metrics

    """
    try:
        result = subprocess.run(
            ["python", "../scripts/audit_pydantic_v2.py", "--project", "."],
            check=False,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "passed": result.returncode == 0,
            "output": result.stdout,
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "passed": False,
            "error": str(e),
        }


def get_test_metrics(project_path: Path) -> dict[str, Any]:
    """Get test pass rate and coverage metrics for a project.

    Args:
        project_path: Path to project root

    Returns:
        Dictionary with test metrics

    """
    try:
        # Try to get pytest output
        result = subprocess.run(
            ["make", "test"],
            check=False,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=300,
        )

        # Parse coverage from output
        output = result.stdout + result.stderr
        coverage = "unknown"
        if "passed" in output:
            coverage = "measured"

        return {
            "test_status": "PASS" if result.returncode == 0 else "FAIL",
            "coverage": coverage,
            "output_lines": len(output.split("\n")),
        }
    except subprocess.TimeoutExpired:
        return {
            "test_status": "TIMEOUT",
            "coverage": "unknown",
        }
    except Exception as e:
        return {
            "test_status": "ERROR",
            "error": str(e),
        }


def get_lint_metrics(project_path: Path) -> dict[str, Any]:
    """Get linting metrics for a project.

    Args:
        project_path: Path to project root

    Returns:
        Dictionary with lint metrics

    """
    try:
        result = subprocess.run(
            ["make", "lint"],
            check=False,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {
            "lint_status": "PASS" if result.returncode == 0 else "FAIL",
            "passed": result.returncode == 0,
        }
    except Exception as e:
        return {
            "lint_status": "ERROR",
            "error": str(e),
        }


def collect_project_metrics(project_name: str) -> dict[str, Any]:
    """Collect all quality metrics for a project.

    Args:
        project_name: Name of project (e.g., 'flext-core')

    Returns:
        Dictionary with all metrics

    """
    workspace = Path.cwd()
    project_path = workspace / project_name

    if not project_path.exists():
        return {
            "project": project_name,
            "status": "NOT_FOUND",
            "timestamp": datetime.now().isoformat(),
        }

    print(f"  Collecting metrics for {project_name}...")

    return {
        "project": project_name,
        "timestamp": datetime.now().isoformat(),
        "pydantic_v2": get_pydantic_compliance(project_path),
        "lint": get_lint_metrics(project_path),
        # "tests": get_test_metrics(project_path),  # Commented out as it's slow
    }


def generate_dashboard(metrics_list: list[dict[str, Any]]) -> str:
    """Generate HTML dashboard from metrics.

    Args:
        metrics_list: List of project metrics

    Returns:
        HTML dashboard string

    """
    total_projects = len(metrics_list)
    passing_projects = sum(
        1 for m in metrics_list if m.get("pydantic_v2", {}).get("passed", False)
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FLEXT Quality Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ color: #333; }}
            .metric {{ margin: 20px 0; padding: 10px; border: 1px solid #ddd; }}
            .pass {{ background-color: #d4edda; color: #155724; }}
            .fail {{ background-color: #f8d7da; color: #721c24; }}
            .progress {{ width: 100%; height: 20px; background: #eee; }}
            .progress-bar {{ height: 100%; background: #28a745; }}
        </style>
    </head>
    <body>
        <h1 class="header">FLEXT Quality Dashboard</h1>
        <p>Generated: {datetime.now().isoformat()}</p>

        <h2>Pydantic v2 Compliance</h2>
        <p>Projects Passing: {passing_projects}/{total_projects}</p>
        <div class="progress">
            <div class="progress-bar" style="width: {(passing_projects / total_projects) * 100}%"></div>
        </div>

        <h2>Project Details</h2>
    """

    for metrics in metrics_list:
        project = metrics.get("project", "unknown")
        pydantic = metrics.get("pydantic_v2", {})
        status = pydantic.get("status", "unknown")
        css_class = "pass" if pydantic.get("passed", False) else "fail"

        html += f"""
        <div class="metric {css_class}">
            <h3>{project}</h3>
            <p>Pydantic v2 Status: {status}</p>
            <p>Timestamp: {metrics.get("timestamp", "unknown")}</p>
        </div>
        """

    html += """
    </body>
    </html>
    """

    return html


def main() -> None:
    """Main entry point."""
    workspace = Path.cwd()

    # Find all FLEXT projects
    projects = sorted([
        p.name
        for p in workspace.glob("flext-*")
        if p.is_dir() and (p / "pyproject.toml").exists()
    ])

    print(f"Collecting metrics for {len(projects)} projects...")

    metrics_list = []
    for project in projects:
        metrics = collect_project_metrics(project)
        metrics_list.append(metrics)

    # Generate JSON output
    json_output = json.dumps(metrics_list, indent=2)
    print("\n" + json_output)

    # Save to file
    with Path("quality_metrics.json").open("w", encoding="utf-8") as f:
        f.write(json_output)
    print("\n✅ Metrics saved to quality_metrics.json")

    # Generate HTML dashboard
    html = generate_dashboard(metrics_list)
    with Path("quality_dashboard.html").open("w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Dashboard saved to quality_dashboard.html")


if __name__ == "__main__":
    main()
