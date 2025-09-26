#!/usr/bin/env python3
"""FLEXT Ecosystem Type Checking Modernization Script.

This script systematically updates all FLEXT projects to:
1. Remove MyPy/PyRight dependencies and configuration
2. Add Pyrefly for unified Python 3.13+ type checking
3. Update Makefile targets to use Pyrefly
4. Add standardized Pyrefly configuration

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from pathlib import Path

import toml

# FLEXT projects to modernize (discovered dynamically)
FLEXT_ROOT = Path("/home/marlonsc/flext")


def find_projects_with_mypy() -> list[Path]:
    """Find all FLEXT projects that have MyPy/PyRight configuration."""
    projects = []

    # Find all pyproject.toml files with mypy/pyright references
    for toml_file in FLEXT_ROOT.rglob("pyproject.toml"):
        # Skip virtual environment and system files
        if ".venv" in str(toml_file) or "site-packages" in str(toml_file):
            continue

        try:
            with Path(toml_file).open(encoding="utf-8") as f:
                content = f.read()
                if "mypy" in content.lower() or "pyright" in content.lower():
                    # Only include FLEXT projects (exclude system packages)
                    project_dir = toml_file.parent
                    if any(
                        part.startswith("flext-")
                        or part
                        in {"client-a-oud-mig", "flexcore", "client-b-meltano-native"}
                        for part in project_dir.parts
                    ):
                        projects.append(project_dir)
        except Exception as e:
            print(f"Warning: Could not read {toml_file}: {e}")

    return sorted(set(projects))


def update_pyproject_toml(project_dir: Path) -> bool:
    """Update pyproject.toml to remove MyPy/PyRight and add Pyrefly."""
    toml_file = project_dir / "pyproject.toml"
    if not toml_file.exists():
        return False

    try:
        # Read current configuration
        with Path(toml_file).open(encoding="utf-8") as f:
            content = f.read()

        # Parse TOML
        data = toml.loads(content)
        modified = False

        # Remove MyPy from dev dependencies
        dev_deps = (
            data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
        )
        if dev_deps:
            original_count = len(dev_deps)
            dev_deps[:] = [dep for dep in dev_deps if not dep.startswith("mypy")]
            if len(dev_deps) < original_count:
                modified = True
                print("  ✅ Removed MyPy from dev dependencies")

        # Remove/update Poetry dev dependencies
        poetry_dev = (
            data.get("tool", {})
            .get("poetry", {})
            .get("group", {})
            .get("dev", {})
            .get("dependencies", {})
        )
        if poetry_dev:
            mypy_keys = [
                key
                for key in poetry_dev
                if "mypy" in key.lower() or "pyre" in key.lower()
            ]
            for key in mypy_keys:
                if key != "pyrefly":  # Keep pyrefly if it exists
                    del poetry_dev[key]
                    modified = True
                    print(f"  ✅ Removed {key} from Poetry dev dependencies")

            # Add pyrefly if not present
            if "pyrefly" not in poetry_dev:
                poetry_dev["pyrefly"] = "^0.34.0"
                modified = True
                print("  ✅ Added Pyrefly to Poetry dev dependencies")

        # Remove MyPy tool configuration
        if "tool" in data:
            tool_keys_to_remove = [
                key
                for key in data["tool"]
                if key in {"mypy", "pydantic-mypy", "pyright"}
            ]
            for key in tool_keys_to_remove:
                del data["tool"][key]
                modified = True
                print(f"  ✅ Removed [tool.{key}] configuration")

        # Add Pyrefly configuration if not present
        if "tool" not in data:
            data["tool"] = {}

        if "pyrefly" not in data["tool"]:
            data["tool"]["pyrefly"] = {
                "python_version": "3.13",
                "target_version": "3.13",
                "show_error_codes": True,
            }
            modified = True
            print("  ✅ Added Pyrefly configuration")

        # Update exclusion lists to include pyrefly_cache
        for tool_name in ["bandit", "deptry", "vulture"]:
            tool_config = data.get("tool", {}).get(tool_name, {})
            if tool_config:
                exclude_key = "exclude_dirs" if tool_name == "bandit" else "exclude"
                if exclude_key in tool_config:
                    excludes = tool_config[exclude_key]
                    if isinstance(excludes, list) and (
                        ".pyrefly_cache" not in excludes
                        and ".pyrefly_cache/" not in excludes
                    ):
                        # Find mypy_cache and add pyrefly_cache after it
                        mypy_idx = next(
                            (
                                i
                                for i, item in enumerate(excludes)
                                if "mypy_cache" in item
                            ),
                            None,
                        )
                        if mypy_idx is not None:
                            cache_entry = (
                                ".pyrefly_cache/"
                                if excludes[mypy_idx].endswith("/")
                                else ".pyrefly_cache"
                            )
                            excludes.insert(mypy_idx + 1, cache_entry)
                            modified = True
                            print(f"  ✅ Added .pyrefly_cache to {tool_name} excludes")

        # Write updated configuration
        if modified:
            with Path(toml_file).open("w", encoding="utf-8") as f:
                toml.dump(data, f)
            return True

        return False

    except Exception as e:
        print(f"  ❌ Error updating {toml_file}: {e}")
        return False


def update_makefile(project_dir: Path) -> bool:
    """Update Makefile to use Pyrefly instead of MyPy."""
    makefile = project_dir / "Makefile"
    if not makefile.exists():
        return False

    try:
        with Path(makefile).open(encoding="utf-8") as f:
            content = f.read()

        # Update type-check target
        original_content = content

        # Replace MyPy commands with Pyrefly
        patterns = [
            (r"mypy\s+\$\(SRC_DIR\)\s+--strict", "pyrefly check $(SRC_DIR)"),
            (
                r"PYTHONPATH=src\s+\$\(POETRY\)\s+run\s+mypy\s+\$\(SRC_DIR\)\s+--strict",
                "$(POETRY) run pyrefly check $(SRC_DIR)",
            ),
            (
                r"\$\(POETRY\)\s+run\s+mypy\s+\$\(SRC_DIR\)\s+--strict",
                "$(POETRY) run pyrefly check $(SRC_DIR)",
            ),
            (r"mypy\s+\.\s+--strict", "pyrefly check src/"),
            (r"mypy\s+src/\s+--strict", "pyrefly check src/"),
        ]

        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                print("  ✅ Updated Makefile type-check target")

        # Update type-check comment if present
        content = re.sub(
            r"## Run type checking$",
            "## Run type checking with Pyrefly",
            content,
            flags=re.MULTILINE,
        )

        # Update clean targets to include pyrefly cache
        if ".mypy_cache/" in content and ".pyrefly_cache/" not in content:
            content = content.replace(".mypy_cache/", ".mypy_cache/ .pyrefly_cache/")
            print("  ✅ Updated Makefile clean targets")

        if content != original_content:
            with Path(makefile).open("w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"  ❌ Error updating {makefile}: {e}")
        return False


def modernize_project(project_dir: Path) -> dict[str, bool]:
    """Modernize a single project's type checking configuration."""
    print(f"\n🔧 Modernizing {project_dir.name}...")

    results = {
        "pyproject_toml": update_pyproject_toml(project_dir),
        "makefile": update_makefile(project_dir),
    }

    if any(results.values()):
        print(f"  ✅ Successfully modernized {project_dir.name}")
    else:
        print(f"  ℹ️  No changes needed for {project_dir.name}")

    return results


def main() -> None:
    """Main function to modernize all FLEXT projects."""
    print("🚀 FLEXT Ecosystem Type Checking Modernization")
    print("=" * 50)
    print("Removing MyPy/PyRight, standardizing on Pyrefly for Python 3.13+")

    # Find all projects with MyPy/PyRight
    projects = find_projects_with_mypy()

    if not projects:
        print("No projects with MyPy/PyRight found.")
        return

    print(f"\nFound {len(projects)} projects with MyPy/PyRight configuration:")
    for project in projects:
        print(f"  • {project.name}")

    # Modernize each project
    total_projects = len(projects)
    successful_projects = 0

    for project_dir in projects:
        try:
            results = modernize_project(project_dir)
            if any(results.values()):
                successful_projects += 1
        except Exception as e:
            print(f"  ❌ Error modernizing {project_dir.name}: {e}")

    # Summary
    print("\n📊 Modernization Summary:")
    print(f"  • Total projects: {total_projects}")
    print(f"  • Successfully modernized: {successful_projects}")
    print(f"  • Unchanged: {total_projects - successful_projects}")

    if successful_projects > 0:
        print(
            f"\n✅ Phase 2 Progress: {successful_projects}/{total_projects} projects modernized"
        )
        print("Next: Run 'poetry lock' in each updated project")
    else:
        print("\nℹ️  All projects already modernized or no changes needed")


if __name__ == "__main__":
    main()
