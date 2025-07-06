#!/usr/bin/env python3
"""
Version Consistency Checker

This script checks that all projects have consistent versions and that
all __version__.py files match their corresponding pyproject.toml files.
"""

import sys
import tomllib
from pathlib import Path

WORKSPACE_ROOT = Path("/home/marlonsc/flext")

# Expected version for all projects
EXPECTED_VERSION = "0.6.0"


def get_version_from_pyproject(project_path: Path) -> str | None:
    """Get version from pyproject.toml file."""
    pyproject_path = project_path / "pyproject.toml"
    if not pyproject_path.exists():
        return None

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        # Check if using dynamic versioning
        if "project" in data and "dynamic" in data["project"]:
            if "version" in data["project"]["dynamic"]:
                return "dynamic"

        # Check for static version
        if "project" in data and "version" in data["project"]:
            return data["project"]["version"]

        return None
    except Exception as e:
        print(f"❌ Failed to read {pyproject_path}: {e}")
        return None


def get_version_from_version_file(project_path: Path, module_name: str) -> str | None:
    """Get version from __version__.py file."""
    version_file_path = project_path / "src" / module_name / "__version__.py"
    if not version_file_path.exists():
        return None

    try:
        with open(version_file_path, encoding="utf-8") as f:
            content = f.read()

        # Extract version using simple string parsing
        for line in content.split("\n"):
            if line.strip().startswith("__version__") and "=" in line:
                # Extract version string
                version_part = line.split("=", 1)[1].strip()
                # Remove quotes
                return version_part.strip("\"'")

        return None
    except Exception as e:
        print(f"❌ Failed to read {version_file_path}: {e}")
        return None


def get_project_module_name(project_name: str) -> str:
    """Convert project name to Python module name."""
    # Special cases for naming conventions
    mapping = {
        "algar-oud-mig": "algar_oud_mig",
        "gruponos-poc-oic-wms": "gruponos_poc_oic_wms",
        "gruponos-meltano-native": "gruponos_meltano_native",
        "flext-meltano-bridge": "flext_meltano_bridge",
    }

    if project_name in mapping:
        return mapping[project_name]

    # For tap/target projects, use the pattern tap_project_name
    if project_name.startswith("flext-tap-"):
        return project_name.replace("flext-tap-", "tap_").replace("-", "_")
    if project_name.startswith("flext-target-"):
        return project_name.replace("flext-target-", "target_").replace("-", "_")
    if project_name.startswith("flext-dbt-"):
        return project_name.replace("flext-dbt-", "dbt_").replace("-", "_")
    # Standard flext projects
    return project_name.replace("-", "_")


def check_project_versions(project_name: str) -> tuple[bool, dict[str, str]]:
    """Check version consistency for a single project."""
    project_path = WORKSPACE_ROOT / project_name
    if not project_path.exists():
        return False, {"error": f"Project {project_name} not found"}

    module_name = get_project_module_name(project_name)

    # Get versions from different sources
    pyproject_version = get_version_from_pyproject(project_path)
    version_file_version = get_version_from_version_file(project_path, module_name)

    status = {
        "pyproject_version": pyproject_version,
        "version_file_version": version_file_version,
        "module_name": module_name,
    }

    # Check consistency
    if pyproject_version == "dynamic":
        # Should have a version file
        if version_file_version is None:
            status["error"] = "Missing __version__.py file for dynamic versioning"
            return False, status

        # Version file should match expected version
        if version_file_version != EXPECTED_VERSION:
            status["error"] = (
                f"Version file has {version_file_version}, expected {EXPECTED_VERSION}"
            )
            return False, status

    elif pyproject_version is not None:
        # Static version should match expected
        if pyproject_version != EXPECTED_VERSION:
            status["error"] = (
                f"pyproject.toml has {pyproject_version}, expected {EXPECTED_VERSION}"
            )
            return False, status

    else:
        status["error"] = "No version found in pyproject.toml"
        return False, status

    return True, status


def main() -> int:
    """Main version checking function."""
    print("🔍 Checking version consistency across FLEXT workspace")
    print(f"📊 Expected version: {EXPECTED_VERSION}")
    print(f"📁 Workspace: {WORKSPACE_ROOT}")

    # All projects to check
    projects = [
        # Core FLEXT projects
        "flext-core",
        "flext-auth",
        "flext-api",
        "flext-grpc",
        "flext-web",
        "flext-cli",
        "flext-plugin",
        "flext-observability",
        "flext-meltano",
        "flext-ldap",
        "flext-db-oracle",
        "flext-quality",
        # Singer/Meltano projects
        "flext-tap-ldap",
        "flext-tap-oracle-oic",
        "flext-tap-oracle-wms",
        "flext-target-ldap",
        "flext-target-oracle",
        "flext-target-oracle-oic",
        "flext-dbt-ldap",
        "flext-oracle-oic-ext",
        # Enterprise projects
        "algar-oud-mig",
        "gruponos-poc-oic-wms",
        "gruponos-meltano-native",
        # Additional projects
        "flext-meltano-bridge",
    ]

    # Also check main workspace
    projects.append(".")  # Main workspace

    successful = 0
    failed = 0
    issues = []

    print(f"\n📦 Checking {len(projects)} projects...\n")

    for project in projects:
        project_name = "workspace" if project == "." else project

        if project == ".":
            # Special handling for main workspace
            project_path = WORKSPACE_ROOT
            pyproject_version = get_version_from_pyproject(project_path)
            version_file_version = get_version_from_version_file(project_path, "flext")

            if (
                pyproject_version == "dynamic"
                and version_file_version == EXPECTED_VERSION
            ):
                print(f"✅ {project_name}: {version_file_version} (dynamic)")
                successful += 1
            else:
                print(f"❌ {project_name}: Issue with versioning")
                issues.append(
                    f"{project_name}: pyproject={pyproject_version}, version_file={version_file_version}"
                )
                failed += 1
        else:
            success, status = check_project_versions(project)

            if success:
                version = status.get(
                    "version_file_version", status.get("pyproject_version", "unknown")
                )
                versioning_type = (
                    "dynamic"
                    if status.get("pyproject_version") == "dynamic"
                    else "static"
                )
                print(f"✅ {project}: {version} ({versioning_type})")
                successful += 1
            else:
                error = status.get("error", "Unknown error")
                print(f"❌ {project}: {error}")
                issues.append(f"{project}: {error}")
                failed += 1

    # Summary
    print("\n📊 Summary:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {successful + failed}")

    if failed > 0:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"   • {issue}")

        print("\n🔧 To fix issues, run:")
        print("   make version-sync")
        return 1
    print(f"\n🎉 All projects have consistent version {EXPECTED_VERSION}!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
