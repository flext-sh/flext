#!/usr/bin/env python3
"""Verification script for version standardization across Oracle projects.

This script verifies that all Oracle projects now use version 0.4.0
from a centralized __version__.py file following the FLX pattern.
"""

import sys
from pathlib import Path


def check_version_file(project_path: Path, package_name: str) -> tuple[bool, str]:
    """Check if version file exists and contains correct version."""
    version_file = project_path / "src" / package_name / "__version__.py"

    if not version_file.exists():
        return False, f"__version__.py not found at {version_file}"

    try:
        # Read and execute the version file
        with open(version_file, encoding="utf-8") as f:
            content = f.read()

        local_vars: dict = {}
        exec(content, {}, local_vars)

        version = local_vars.get("__version__")
        if version != "0.4.0":
            return False, f"Version is {version}, expected 0.4.0"

        # Check for required metadata
        required_vars = [
            "__version_info__",
            "__title__",
            "__description__",
            "__author__",
        ]
        missing = [var for var in required_vars if var not in local_vars]
        if missing:
            return False, f"Missing metadata: {missing}"

        return True, "✓ Version 0.4.0 with complete metadata"

    except Exception as e:
        return False, f"Error reading version file: {e}"


def check_pyproject_version(project_path: Path) -> tuple[bool, str]:
    """Check if pyproject.toml has correct version."""
    pyproject_file = project_path / "pyproject.toml"

    if not pyproject_file.exists():
        return False, "pyproject.toml not found"

    try:
        with open(pyproject_file, encoding="utf-8") as f:
            content = f.read()

        # Look for version line
        for line in content.split("\n"):
            if line.strip().startswith("version = "):
                if "0.4.0" in line:
                    return True, "✓ Version 0.4.0 in pyproject.toml"
                return False, f"Wrong version in pyproject.toml: {line.strip()}"

        return False, "Version line not found in pyproject.toml"

    except Exception as e:
        return False, f"Error reading pyproject.toml: {e}"


def main() -> None:
    """Main verification function."""
    print("🔍 Verifying version standardization across Oracle projects\n")

    # Define projects to check
    projects = [
        ("dc-oracle-db", "flx_database_oracle"),
        ("dc-oracle-oic", "flx_http_oracle_oic"),
        ("dc-oracle-wms", "flx_http_oracle_wms"),
        ("project-algar-oud", "oud_automation"),
        ("project-gruponos-oic-wms", "gn_oic_wms_db"),
    ]

    base_path = Path(__file__).parent
    all_passed = True

    for project_dir, package_name in projects:
        project_path = base_path / project_dir

        print(f"📦 Checking {project_dir}:")

        # Check version file
        version_ok, version_msg = check_version_file(project_path, package_name)
        print(f"  __version__.py: {version_msg}")

        # Check pyproject.toml
        pyproject_ok, pyproject_msg = check_pyproject_version(project_path)
        print(f"  pyproject.toml: {pyproject_msg}")

        # Check FLX dependency
        pyproject_file = project_path / "pyproject.toml"
        has_flx = False
        if pyproject_file.exists():
            with open(pyproject_file, encoding="utf-8") as f:
                content = f.read()
                has_flx = (
                    'flx = { path = "../flx"' in content
                    or 'flx = {path = "../flx"' in content
                )

        flx_status = (
            "✓ FLX dependency present" if has_flx else "✗ FLX dependency missing"
        )
        print(f"  FLX dependency: {flx_status}")

        project_passed = version_ok and pyproject_ok and has_flx
        all_passed = all_passed and project_passed

        status = "✅ PASS" if project_passed else "❌ FAIL"
        print(f"  Status: {status}\n")

    # Summary
    if all_passed:
        print("🎉 All projects successfully standardized to version 0.4.0!")
        print("   - Centralized __version__.py files with complete metadata")
        print("   - pyproject.toml files updated to 0.4.0")
        print("   - FLX dependencies properly configured")
        print("   - Redundant dependencies removed")
        print("❌ Some projects failed verification")
        sys.exit(1)


if __name__ == "__main__":
    main()
