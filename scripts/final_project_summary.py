#!/usr/bin/env python
"""
Final comprehensive validation and summary.

Per CLAUDE.md RULE 4: Complete delivery with zero tolerance for violations.
Test ALL 21 projects and provide final status summary.
"""

import subprocess
from pathlib import Path


def test_project_import(project_name: str) -> tuple[bool, str]:
    """Test if project module can be imported."""
    project_path = Path(f"/home/marlonsc/pyauto/{project_name}")
    src_path = project_path / "src"
    module_name = project_name.replace("-", "_")

    try:
        result = subprocess.run(
            [
                "python",
                "-c",
                f"import sys; sys.path.insert(0, '{src_path}'); import {module_name}; print('✅ Success')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return True, "Import successful"
        return False, f"Import error: {result.stderr.strip()}"

    except Exception as e:
        return False, f"Test error: {e}"


def get_submodules() -> list[str]:
    """Get all git submodules."""
    try:
        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd="/home/marlonsc/pyauto",
            capture_output=True,
            text=True,
            check=True,
        )
        submodules = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    submodules.append(parts[1])
        return sorted(submodules)
    except subprocess.CalledProcessError:
        return []


def main():
    """Run final comprehensive validation."""

    submodules = get_submodules()
    working_projects = []
    broken_projects = []

    for project_name in submodules:
        import_success, import_msg = test_project_import(project_name)

        if import_success:
            working_projects.append(project_name)
        else:
            broken_projects.append((project_name, import_msg))

    if len(working_projects) == len(submodules):
        status = "ALL_PROJECTS_WORKING"
    else:
        for _name, _error in broken_projects:
            pass
        status = f"PARTIAL_SUCCESS_{len(working_projects)}_OF_{len(submodules)}"

    # Log to token
    with open("/home/marlonsc/pyauto/.token", "a") as f:
        f.write(
            f"FINAL-VALIDATION-005 {status}: {len(working_projects)}/{len(submodules)} projects working\n"
        )

    return len(working_projects) == len(submodules)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
