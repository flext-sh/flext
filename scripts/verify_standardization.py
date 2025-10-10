#!/usr/bin/env python3
"""Verify __version__.py standardization across FLEXT ecosystem.

This script validates that all projects correctly use pyproject.toml as the
single source of truth for metadata via importlib.metadata.

Copyright (c) 2025 client-a Telecom. Todos os direitos reservados.
SPDX-License-Identifier: Proprietary
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Final

FLEXT_ROOT: Final[Path] = Path("/home/marlonsc/flext")


def verify_version_file(project_dir: Path, package_name: str) -> dict[str, bool]:
    """Verify __version__.py follows standards.

    Args:
        project_dir: Project directory path
        package_name: Package name

    Returns:
        Dictionary of verification checks

    """
    results = {
        "has_version_file": False,
        "uses_importlib": False,
        "no_hardcoded_version": False,
        "exports_all_metadata": False,
    }

    version_file = project_dir / "src" / package_name / "__version__.py"

    if not version_file.exists():
        return results

    results["has_version_file"] = True

    content = version_file.read_text()

    # Check uses importlib.metadata
    if "from importlib.metadata import metadata" in content:
        results["uses_importlib"] = True

    # Check no hardcoded __version__ = "x.y.z"
    if not re.search(r'__version__\s*=\s*["\'][\d.]+["\']', content):
        results["no_hardcoded_version"] = True

    # Check exports all metadata
    required_exports = [
        "__version__",
        "__version_info__",
        "__title__",
        "__description__",
        "__author__",
        "__author_email__",
        "__license__",
        "__url__",
    ]
    has_all_exports = all(export in content for export in required_exports)
    results["exports_all_metadata"] = has_all_exports

    return results


def verify_init_file(project_dir: Path, package_name: str) -> dict[str, bool]:
    """Verify __init__.py imports from __version__.

    Args:
        project_dir: Project directory path
        package_name: Package name

    Returns:
        Dictionary of verification checks

    """
    results = {
        "imports_from_version": False,
        "no_hardcoded_version": False,
    }

    init_file = project_dir / "src" / package_name / "__init__.py"

    if not init_file.exists():
        return results

    content = init_file.read_text()

    # Check imports from __version__
    if f"from {package_name}.__version__ import" in content:
        results["imports_from_version"] = True

    # Check no hardcoded __version__ = "x.y.z"
    if not re.search(r'__version__\s*=\s*["\'][\d.]+["\']', content):
        results["no_hardcoded_version"] = True

    return results


def verify_constants_file(project_dir: Path, package_name: str) -> dict[str, bool]:
    """Verify constants.py uses importlib.metadata if present.

    Args:
        project_dir: Project directory path
        package_name: Package name

    Returns:
        Dictionary of verification checks

    """
    results = {
        "no_hardcoded_metadata": True,
    }

    constants_file = project_dir / "src" / package_name / "constants.py"

    if not constants_file.exists():
        return results

    content = constants_file.read_text()

    # Check for hardcoded metadata
    hardcoded_patterns = [
        (r'^\s*VERSION\s*=\s*["\'][\d.]+["\']', "VERSION"),
        (r'^\s*AUTHOR\s*=\s*["\']', "AUTHOR"),
        (r'^\s*DESCRIPTION\s*=\s*["\']', "DESCRIPTION"),
        (r'^\s*LICENSE\s*=\s*["\']', "LICENSE"),
    ]

    for pattern, _name in hardcoded_patterns:
        if re.search(pattern, content, re.MULTILINE):
            # Check if it's using __version__ variable instead
            if "VERSION = __version__" not in content:
                results["no_hardcoded_metadata"] = False
                break

    return results


def verify_project(project_dir: Path) -> dict[str, object]:
    """Verify a single project.

    Args:
        project_dir: Project directory path

    Returns:
        Verification results

    """
    # Find package directory
    src_dir = project_dir / "src"
    if not src_dir.exists():
        return {"error": "No src/ directory"}

    package_name = project_dir.name.replace("-", "_")
    package_dir = src_dir / package_name

    if not package_dir.exists():
        # Try to find any package directory
        package_dirs = [
            d for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]
        if not package_dirs:
            return {"error": "No package directory"}

        # For multi-package projects, use the main one
        package_dir = package_dirs[0]
        package_name = package_dir.name

    results = {
        "project": project_dir.name,
        "package": package_name,
        "version_file": verify_version_file(project_dir, package_name),
        "init_file": verify_init_file(project_dir, package_name),
        "constants_file": verify_constants_file(project_dir, package_name),
    }

    # Calculate overall status
    version_ok = all(results["version_file"].values())
    init_ok = all(results["init_file"].values())
    constants_ok = results["constants_file"]["no_hardcoded_metadata"]

    results["status"] = "✅" if (version_ok and init_ok and constants_ok) else "⚠️"

    return results


def main() -> None:
    """Verify all projects."""
    print("=" * 80)
    print("🔍 Verifying __version__.py Standardization Across FLEXT Ecosystem")
    print("=" * 80)

    all_projects = []

    # Find all projects with pyproject.toml
    for project_dir in sorted(FLEXT_ROOT.iterdir()):
        if not project_dir.is_dir():
            continue

        pyproject_file = project_dir / "pyproject.toml"
        if not pyproject_file.exists():
            continue

        all_projects.append(project_dir)

    print(f"\n📊 Verifying {len(all_projects)} projects...\n")

    success_count = 0
    warning_count = 0
    issues: list[str] = []

    for project_dir in all_projects:
        result = verify_project(project_dir)

        if "error" in result:
            print(f"❌ {project_dir.name}: {result['error']}")
            warning_count += 1
            continue

        status = result["status"]
        project = result["project"]

        if status == "✅":
            print(f"{status} {project}")
            success_count += 1
        else:
            print(f"{status} {project}")
            warning_count += 1

            # Report specific issues
            if not result["version_file"]["has_version_file"]:
                issues.append(f"  • {project}: Missing __version__.py")
            elif not result["version_file"]["uses_importlib"]:
                issues.append(
                    f"  • {project}: __version__.py doesn't use importlib.metadata"
                )
            elif not result["version_file"]["no_hardcoded_version"]:
                issues.append(f"  • {project}: __version__.py has hardcoded version")

            if not result["init_file"]["imports_from_version"]:
                issues.append(
                    f"  • {project}: __init__.py doesn't import from __version__"
                )
            if not result["init_file"]["no_hardcoded_version"]:
                issues.append(f"  • {project}: __init__.py has hardcoded version")

            if not result["constants_file"]["no_hardcoded_metadata"]:
                issues.append(f"  • {project}: constants.py has hardcoded metadata")

    print("\n" + "=" * 80)
    print("📈 Verification Summary")
    print("=" * 80)
    print(f"\nTotal projects: {len(all_projects)}")
    print(f"✅ Fully standardized: {success_count}")
    print(f"⚠️  Need attention: {warning_count}")

    if issues:
        print(f"\n⚠️  Issues Found ({len(issues)}):")
        for issue in issues:
            print(issue)

    print("\n" + "=" * 80)

    if warning_count == 0:
        print("✅ ALL PROJECTS FULLY STANDARDIZED!")
        sys.exit(0)
    else:
        print(f"⚠️  {warning_count} projects need attention")
        sys.exit(1)


if __name__ == "__main__":
    main()
