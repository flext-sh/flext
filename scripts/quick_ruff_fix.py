#!/usr/bin/env python
"""Quick targeted ruff fix for critical projects."""

import subprocess
from pathlib import Path

# Priority projects to fix first
PRIORITY_PROJECTS = [
    "flx-ldap",  # 532 violations
    "tap-ldap",
    "target-ldap",
    "ldap-core-shared",
    "dbt-ldap",
]


def quick_fix_project(project_name: str) -> None:
    """Quick fix a single project."""
    project_path = Path(f"/home/marlonsc/pyauto/{project_name}")

    if not project_path.exists():
        return

    # Run ruff fix with aggressive settings
    try:
        # First pass - safe fixes
        subprocess.run(
            ["poetry", "run", "ruff", "check", ".", "--fix"],
            cwd=project_path,
            capture_output=True,
            timeout=30,
        )

        # Second pass - unsafe fixes
        subprocess.run(
            ["poetry", "run", "ruff", "check", ".", "--fix", "--unsafe-fixes"],
            cwd=project_path,
            capture_output=True,
            timeout=30,
        )

        # Format with black
        subprocess.run(
            ["poetry", "run", "black", "."],
            cwd=project_path,
            capture_output=True,
            timeout=30,
        )

        # Check remaining violations
        result = subprocess.run(
            ["poetry", "run", "ruff", "check", ".", "--quiet"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        remaining = len([l for l in result.stdout.split("\n") if l.strip()])

        if remaining == 0:
            pass

    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass


if __name__ == "__main__":
    for project in PRIORITY_PROJECTS:
        quick_fix_project(project)
