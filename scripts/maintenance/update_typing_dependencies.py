#!/usr/bin/env python3
"""Update typing dependencies across all pyproject.toml files.

This script ensures consistent typing dependencies and mypy configuration
across all projects in the PyAuto workspace.
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import toml
import yaml


@dataclass
class TypingConfig:
    """Configuration for typing dependencies."""

    python_version: str
    python_minimum: str
    core_typing: dict[str, str]
    stdlib_types: dict[str, str]
    web_types: dict[str, str]
    database_types: dict[str, str]
    dev_types: dict[str, str]
    async_types: dict[str, str]
    project_mappings: dict[str, list[str]]
    mypy_config: dict[str, Any]
    projects: dict[str, dict[str, list[str]]]


def load_typing_config(config_path: Path) -> TypingConfig:
    """Load typing configuration from YAML file."""
    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return TypingConfig(
        python_version=data["python_version"],
        python_minimum=data["python_minimum"],
        core_typing=data["core_typing"],
        stdlib_types=data["stdlib_types"],
        web_types=data["web_types"],
        database_types=data["database_types"],
        dev_types=data["dev_types"],
        async_types=data["async_types"],
        project_mappings=data["project_mappings"],
        mypy_config=data["mypy_config"],
        projects=data["projects"],
    )


def get_all_type_deps(config: TypingConfig) -> dict[str, str]:
    """Get all available type dependencies."""
    all_deps = {}
    all_deps.update(config.core_typing)
    all_deps.update(config.stdlib_types)
    all_deps.update(config.web_types)
    all_deps.update(config.database_types)
    all_deps.update(config.dev_types)
    all_deps.update(config.async_types)
    return all_deps


def determine_project_type(project_path: Path) -> str:
    """Determine project type based on path and content."""
    project_name = project_path.name

    # Check specific project mappings
    if project_name == "flx":
        return "flx"
    if "database" in project_name:
        return "flx-database-oracle"
    if "http" in project_name:
        if "oic" in project_name:
            return "flx-http-oracle-oic"
        return "flx-http-oracle-wms"
    if "meltano" in project_name:
        return "flx-meltano-enterprise"
    if "client-a" in project_name:
        return "client-a-oud-mig"
    if "ldap" in project_name:
        return "ldap-projects"
    if any(x in project_name for x in ["oracle", "tap-", "target-"]):
        if "oracle" in project_name:
            return "oracle-projects"
        return "tap-target-projects"
    return "pyauto-root"


def get_required_deps(config: TypingConfig, project_type: str) -> dict[str, str]:
    """Get required dependencies for project type."""
    if project_type not in config.projects:
        project_type = "pyauto-root"

    required_groups = config.projects[project_type]["types"]
    all_deps = get_all_type_deps(config)
    required_deps = {}

    for group in required_groups:
        if group in config.project_mappings:
            for dep_name in config.project_mappings[group]:
                # Convert name to package name (remove types- prefix for core deps)
                if dep_name in all_deps:
                    required_deps[dep_name] = all_deps[dep_name]

    return required_deps


def update_pyproject_toml(
    pyproject_path: Path,
    config: TypingConfig,
    dry_run: bool = False,
) -> bool:
    """Update a single pyproject.toml file."""
    try:
        with open(pyproject_path, encoding="utf-8") as f:
            data = toml.load(f)
    except Exception as e:
        print(f"❌ Error reading {pyproject_path}: {e}")
        return False

    project_type = determine_project_type(pyproject_path.parent)
    required_deps = get_required_deps(config, project_type)

    changes_made = False

    # Update Poetry dependencies
    if "tool" in data and "poetry" in data["tool"]:
        poetry_data = data["tool"]["poetry"]

        # Add typing-extensions to main dependencies if not present
        if "dependencies" in poetry_data:
            deps = poetry_data["dependencies"]
            if "typing-extensions" in required_deps and "typing-extensions" not in deps:
                deps["typing-extensions"] = required_deps["typing-extensions"]
                changes_made = True
                print("  + Added typing-extensions to main dependencies")

        # Update dev dependencies
        if "group" in poetry_data and "dev" in poetry_data["group"]:
            dev_deps = poetry_data["group"]["dev"].get("dependencies", {})
        else:
            if "group" not in poetry_data:
                poetry_data["group"] = {}
            if "dev" not in poetry_data["group"]:
                poetry_data["group"]["dev"] = {}
            if "dependencies" not in poetry_data["group"]["dev"]:
                poetry_data["group"]["dev"]["dependencies"] = {}
            dev_deps = poetry_data["group"]["dev"]["dependencies"]

        # Add/update required typing dependencies
        for dep_name, version in required_deps.items():
            if dep_name == "typing-extensions":
                continue  # Already handled in main deps

            if dep_name not in dev_deps or dev_deps[dep_name] != version:
                dev_deps[dep_name] = version
                changes_made = True
                print(f"  + Updated {dep_name} = {version}")

    # Update mypy configuration
    if "tool" not in data:
        data["tool"] = {}

    if "mypy" not in data["tool"]:
        data["tool"]["mypy"] = {}

    mypy_section = data["tool"]["mypy"]

    # Update mypy config
    for key, value in config.mypy_config.items():
        if key not in mypy_section or mypy_section[key] != value:
            mypy_section[key] = value
            changes_made = True
            print(f"  + Updated mypy.{key} = {value}")

    # Add standard mypy overrides
    if "overrides" not in mypy_section:
        mypy_section["overrides"] = []

    # Standard override for missing imports
    standard_overrides: list[dict[str, Any]] = [
        {
            "module": ["oracledb.*", "ldap.*", "ldif.*", "singer.*", "meltano.*"],
            "ignore_missing_imports": True,
        },
        {
            "module": ["tests.*", "conftest"],
            "ignore_errors": False,
            "disallow_untyped_defs": False,
        },
    ]

    # Check if overrides need to be added/updated
    existing_modules = {
        tuple(override.get("module", [])) for override in mypy_section["overrides"]
    }

    for override in standard_overrides:
        override_modules: tuple[str, ...] = tuple(override["module"])
        if override_modules not in existing_modules:
            mypy_section["overrides"].append(override)
            changes_made = True
            print(f"  + Added mypy override for {override['module']}")

    if changes_made and not dry_run:
        try:
            with open(pyproject_path, "w", encoding="utf-8") as f:
                toml.dump(data, f)
            print(f"✅ Updated {pyproject_path}")
        except Exception as e:
            print(f"❌ Error writing {pyproject_path}: {e}")
            return False
    elif changes_made and dry_run:
        print(f"🔍 Would update {pyproject_path}")
    else:
        print(f"⚡ No changes needed for {pyproject_path}")

    return True


def find_pyproject_files(root_path: Path) -> list[Path]:
    """Find all pyproject.toml files, excluding backups and .venv."""
    pyproject_files = []

    for pyproject_path in root_path.rglob("pyproject.toml"):
        # Skip backup directories and virtual environments
        if any(
            part in str(pyproject_path)
            for part in ["backups", ".venv", "site-packages"]
        ):
            continue
        pyproject_files.append(pyproject_path)

    return sorted(pyproject_files)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Update typing dependencies across PyAuto workspace",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/typing-dependencies.yaml"),
        help="Path to typing configuration file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--project",
        type=str,
        help="Update only specific project (directory name)",
    )

    args = parser.parse_args()

    if not args.config.exists():
        print(f"❌ Configuration file not found: {args.config}")
        return 1

    try:
        config = load_typing_config(args.config)
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return 1

    root_path = Path.cwd()
    pyproject_files = find_pyproject_files(root_path)

    if args.project:
        # Filter to specific project
        pyproject_files = [p for p in pyproject_files if args.project in str(p)]

    if not pyproject_files:
        print("❌ No pyproject.toml files found")
        return 1

    print(f"🔍 Found {len(pyproject_files)} pyproject.toml files")

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")

    success_count = 0

    for pyproject_path in pyproject_files:
        print(f"\n📦 Processing {pyproject_path}")
        if update_pyproject_toml(pyproject_path, config, args.dry_run):
            success_count += 1

    print(f"\n✅ Successfully processed {success_count}/{len(pyproject_files)} files")

    if success_count == len(pyproject_files):
        print("🎉 All projects updated successfully!")
        return 0
    print("⚠️  Some projects had issues")
    return 1


if __name__ == "__main__":
    sys.exit(main())
