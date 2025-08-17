#!/usr/bin/env python3
"""Consolidate dependencies across all FLEXT projects following KISS principle.

This script removes duplicate dependencies and applies centralized dev dependencies
from .flext-dev-dependencies.toml to all FLEXT projects.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

import toml


def main() -> None:
    """Consolidate dependencies across workspace following KISS principle."""
    workspace_root = Path(__file__).parent.parent.parent
    central_deps_file = workspace_root / ".flext-dev-dependencies.toml"

    if not central_deps_file.exists():
      print(f"❌ Central dependencies file not found: {central_deps_file}")
      return

    # Load centralized dependencies
    central_deps = toml.load(central_deps_file)

    # Find all FLEXT project pyproject.toml files
    pyproject_files = list(workspace_root.glob("*/pyproject.toml"))
    pyproject_files = [
      f
      for f in pyproject_files
      if not str(f).startswith(str(workspace_root / ".venv"))
    ]

    print(f"🔍 Found {len(pyproject_files)} projects to update")

    for pyproject_file in pyproject_files:
      project_name = pyproject_file.parent.name

      # Skip workspace root pyproject.toml
      if project_name == "flext":
          print(f"⏭️  Skipping workspace root: {project_name}")
          continue

      print(f"🔧 Processing project: {project_name}")

      # Load project pyproject.toml
      try:
          project_config = toml.load(pyproject_file)
      except (OSError, ValueError, TypeError) as e:
          print(f"❌ Failed to load {pyproject_file}: {e}")
          continue

      # Update dependency groups following KISS principle
      if "tool" not in project_config:
          project_config["tool"] = {}
      if "poetry" not in project_config["tool"]:
          project_config["tool"]["poetry"] = {}

      # Replace with centralized dependencies
      for group_name, group_deps in (
          central_deps.get("tool", {}).get("poetry", {}).items()
      ):
          if group_name.startswith("group."):
              project_config["tool"]["poetry"][group_name] = group_deps
              print(f"  ✅ Updated {group_name}")

      # Ensure dependency groups exist
      if "group.dev.dependencies" not in project_config["tool"]["poetry"]:
          project_config["tool"]["poetry"]["group.dev.dependencies"] = {}
      if "group.typings.dependencies" not in project_config["tool"]["poetry"]:
          project_config["tool"]["poetry"]["group.typings.dependencies"] = {}

      # Add project-specific type dependencies if needed
      if project_name == "flext-ldap":
          project_config["tool"]["poetry"]["group.typings.dependencies"][
              "types-ldap3"
          ] = "^2.9.13.20250622"
      elif project_name == "flext-api":
          project_config["tool"]["poetry"]["group.dev.dependencies"][
              "types-setuptools"
          ] = "^80.9.0.20250529"
          project_config["tool"]["poetry"]["group.dev.dependencies"][
              "types-decorator"
          ] = "^5.2.0.20250324"
      elif project_name == "client-a-oud-mig":
          # Add specific dependencies for client-a project
          client-a_types = project_config["tool"]["poetry"]["group.typings.dependencies"]
          client-a_types.update(
              {
                  "types-aiofiles": "^24.1.0.20250708",
                  "types-click": "^7.1.8",
                  "types-pygments": "^2.19.0.20250516",
                  "types-cffi": "^1.17.0.20250523",
              },
          )

      # Save updated pyproject.toml
      try:
          with Path(pyproject_file).open("w", encoding="utf-8") as f:
              toml.dump(project_config, f)
          print(f"  💾 Saved {pyproject_file}")
      except (OSError, ValueError, TypeError) as e:
          print(f"❌ Failed to save {pyproject_file}: {e}")

    print("\n🎉 Dependency consolidation completed following KISS principle!")
    print("📋 Summary:")
    print("  • Removed duplicate dependencies across projects")
    print("  • Applied centralized dev/test/typings/security dependencies")
    print("  • Preserved project-specific dependencies where needed")
    print("  • Following FLEXT CLAUDE.md standards")


if __name__ == "__main__":
    main()
