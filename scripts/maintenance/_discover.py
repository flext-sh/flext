#!/usr/bin/env python3
# Owner-Skill: .claude/skills/workspace-maintenance/SKILL.md
"""Unified project discovery for FLEXT workspace — single source of truth.

Mirrors the exact discovery logic from the root Makefile:
  1. FLEXT_PROJECTS: Parse .gitmodules for 'path = flext-*' entries, verify pyproject.toml
  2. EXTERNAL_PROJECTS: Dirs with pyproject.toml that reference flext-core/flext_core
     but are NOT listed in .gitmodules
  3. ALL_PROJECTS = FLEXT_PROJECTS + EXTERNAL_PROJECTS

This module is standalone (stdlib only) and importable by all maintenance scripts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectInfo:
    """Discovered project metadata."""

    path: Path
    name: str
    kind: str  # "submodule" or "external"
    has_pyproject: bool = True


def _parse_gitmodules(workspace_root: Path) -> set[str]:
    """Parse .gitmodules to extract submodule path names."""
    gitmodules = workspace_root / ".gitmodules"
    if not gitmodules.exists():
        return set()

    try:
        content = gitmodules.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()

    # Match: path = <name>
    return set(re.findall(r"^\s*path\s*=\s*(.+?)\s*$", content, re.MULTILINE))


def _is_flext_core_consumer(pyproject_path: Path) -> bool:
    """Check if a pyproject.toml references flext-core or flext_core."""
    try:
        content = pyproject_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return "flext-core" in content or "flext_core" in content


def discover_flext_projects(workspace_root: Path) -> list[ProjectInfo]:
    """Discover flext-* submodule projects (phase 1 — mirrors Makefile FLEXT_PROJECTS).

    Logic: grep .gitmodules for 'path = flext-*', verify pyproject.toml exists.
    """
    submodule_paths = _parse_gitmodules(workspace_root)
    projects: list[ProjectInfo] = []

    for name in sorted(submodule_paths):
        if not name.startswith("flext-"):
            continue
        project_dir = workspace_root / name
        if project_dir.is_dir() and (project_dir / "pyproject.toml").exists():
            projects.append(ProjectInfo(path=project_dir, name=name, kind="submodule"))

    return projects


def discover_external_projects(workspace_root: Path) -> list[ProjectInfo]:
    """Discover external projects that consume flext-core (phase 2 — mirrors Makefile EXTERNAL_PROJECTS).

    Logic: dirs with pyproject.toml + references flext-core + NOT in .gitmodules.
    Examples: client-a-oud-mig, client-b-meltano-native.
    """
    submodule_paths = _parse_gitmodules(workspace_root)
    projects: list[ProjectInfo] = []

    for item in sorted(workspace_root.iterdir()):
        if not item.is_dir():
            continue
        name = item.name
        # Skip hidden dirs, __pycache__, common non-project dirs
        if name.startswith(".") or name.startswith("_"):
            continue
        # Skip if it's a submodule
        if name in submodule_paths:
            continue
        # Must have pyproject.toml
        pyproject = item / "pyproject.toml"
        if not pyproject.exists():
            continue
        # Must reference flext-core
        if not _is_flext_core_consumer(pyproject):
            continue

        projects.append(ProjectInfo(path=item, name=name, kind="external"))

    return projects


def discover_all_projects(workspace_root: Path) -> list[ProjectInfo]:
    """Discover ALL workspace projects — submodules + external (mirrors Makefile ALL_PROJECTS).

    This is the canonical entry point. Returns projects sorted by name.
    """
    flext = discover_flext_projects(workspace_root)
    external = discover_external_projects(workspace_root)
    return sorted(flext + external, key=lambda p: p.name)


def discover_all_paths(workspace_root: Path) -> list[Path]:
    """Convenience: return just the Path list for backward compatibility."""
    return [p.path for p in discover_all_projects(workspace_root)]


# ---------------------------------------------------------------------------
# CLI: run standalone to verify discovery matches `make discover`
# ---------------------------------------------------------------------------


def main() -> int:
    """Print discovered projects (matches `make discover` output)."""
    import sys

    root = Path.cwd()
    flext = discover_flext_projects(root)
    external = discover_external_projects(root)
    all_projects = discover_all_projects(root)

    print(f"=== FLEXT Submodule Projects ({len(flext)}) ===")
    for p in flext:
        print(f"  {p.name}")

    print(f"\n=== External Projects ({len(external)}) ===")
    for p in external:
        print(f"  {p.name}")

    print(f"\n=== Total: {len(all_projects)} Python projects ===")

    # Verify against make discover count
    expected_flext = 29
    expected_external = 2
    if len(flext) != expected_flext or len(external) != expected_external:
        print(
            f"\nWARNING: Expected {expected_flext} flext + {expected_external} external, "
            f"got {len(flext)} + {len(external)}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
