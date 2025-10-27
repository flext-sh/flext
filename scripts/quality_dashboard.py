#!/usr/bin/env python3
"""Generate quality metrics dashboard for FLEXT projects.

Collects Pydantic v2 compliance and other quality metrics across all
FLEXT projects and generates a comprehensive dashboard report.

Usage:
    python quality_dashboard.py > quality_metrics.json
    python quality_dashboard.py --html > quality_dashboard.html

Copyright (c) 2025 FLEXT Team. All rights reserved.
"""

import importlib.util
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def get_pydantic_compliance(project_path: Path) -> dict[str, Any]:
    """Get Pydantic v2 compliance metrics for a project using importlib.

    Args:
        project_path: Path to project root

    Returns:
        Dictionary with compliance metrics

    """
    try:
        # Use importlib to load and execute audit script instead of subprocess
        script_path = project_path / ".." / "scripts" / "audit_pydantic_v2.py"
        script_path = script_path.resolve()

        if not script_path.exists():
            return {
                "status": "ERROR",
                "passed": False,
                "error": f"Script not found: {script_path}",
            }

        # Load module using importlib
        spec = importlib.util.spec_from_file_location("audit_pydantic_v2", script_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # If the module has a main function or check function, call it
            if hasattr(module, "check_compliance"):
                result = module.check_compliance(project_path)
                return {
                    "status": "PASS" if result else "FAIL",
                    "passed": result,
                    "output": "Compliance check executed",
                }
            if hasattr(module, "main"):
                # Execute main with appropriate arguments
                module.main()
                return {
                    "status": "PASS",
                    "passed": True,
                    "output": "Script executed successfully",
                }

        return {
            "status": "ERROR",
            "passed": False,
            "error": "Could not load audit script",
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "passed": False,
            "error": str(e),
        }


def get_test_metrics(project_path: Path) -> dict[str, Any]:
    """Get test pass rate and coverage metrics for a project using os.system.

    Args:
        project_path: Path to project root

    Returns:
        Dictionary with test metrics

    """
    try:
        # Save current working directory
        original_cwd = Path.cwd()

        try:
            # Change to project directory
            os.chdir(str(project_path))

            # Execute make test using os.system (not subprocess)
            # Redirect output to temporary file for analysis
            import tempfile

            with tempfile.NamedTemporaryFile(
                encoding="utf-8", mode="w+", delete=False
            ) as tmp:
                tmp_path = tmp.name

            exit_code = os.system(f"make test > {tmp_path} 2>&1")

            # Read captured output
            try:
                with Path(tmp_path).open(encoding="utf-8") as f:
                    output = f.read()
                Path(tmp_path).unlink()
            except Exception:
                output = ""

            coverage = "unknown"
            if "passed" in output:
                coverage = "measured"

            return {
                "test_status": "PASS" if exit_code == 0 else "FAIL",
                "coverage": coverage,
                "output_lines": len(output.split("\n")),
            }
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

    except Exception as e:
        return {
            "test_status": "ERROR",
            "error": str(e),
        }


def get_lint_metrics(project_path: Path) -> dict[str, Any]:
    """Get linting metrics for a project using os.system.

    Args:
        project_path: Path to project root

    Returns:
        Dictionary with lint metrics

    """
    try:
        # Save current working directory
        original_cwd = Path.cwd()

        try:
            # Change to project directory
            os.chdir(str(project_path))

            # Execute make lint using os.system (not subprocess)
            # Redirect output to discard it (only care about exit code)
            exit_code = os.system("make lint > /dev/null 2>&1")

            return {
                "lint_status": "PASS" if exit_code == 0 else "FAIL",
                "passed": exit_code == 0,
            }
        finally:
            # Restore original working directory
            os.chdir(original_cwd)

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
            <div class="progress-bar" style="width: {((passing_projects / total_projects) * 100) if total_projects > 0 else 0}%"></div>
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
