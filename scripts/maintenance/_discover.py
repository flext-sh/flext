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
    """Discover submodule projects (phase 1 — all .gitmodules entries with pyproject.toml).

    Logic: parse .gitmodules for all path = ... entries, verify pyproject.toml exists.
    Includes flext-* and flexcore (and any future submodule with pyproject.toml).
    """
    submodule_paths = _parse_gitmodules(workspace_root)
    projects: list[ProjectInfo] = []

    for name in sorted(submodule_paths):
        project_dir = workspace_root / name
        if project_dir.is_dir() and (project_dir / "pyproject.toml").exists():
            projects.append(ProjectInfo(path=project_dir, name=name, kind="submodule"))

    return projects


def discover_external_projects(workspace_root: Path) -> list[ProjectInfo]:
    """Discover external projects that consume flext-core (phase 2 — mirrors Makefile EXTERNAL_PROJECTS).

    Logic: dirs with pyproject.toml + references flext-core + NOT in .gitmodules.
    """
    submodule_paths = _parse_gitmodules(workspace_root)
    projects: list[ProjectInfo] = []

    for item in sorted(workspace_root.iterdir()):
        if not item.is_dir():
            continue
        name = item.name
        # Skip hidden dirs, __pycache__, common non-project dirs
        if name.startswith((".", "_")):
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
# CLI: run standalone; consumable by Makefile via --kind/--format
# ---------------------------------------------------------------------------


def main() -> int:
    """Print discovered projects; supports --kind/--format for Makefile consumption."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Unified project discovery for FLEXT workspace (single source of truth)."
    )
    parser.add_argument(
        "--kind",
        choices=("submodule", "external", "all"),
        default=None,
        help="Output only submodule, external, or all projects.",
    )
    parser.add_argument(
        "--format",
        choices=("human", "makefile"),
        default="human",
        help="human: report; makefile: space-separated names for $(shell ...).",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        metavar="DIR",
        help="Workspace root (default: cwd).",
    )
    args = parser.parse_args()

    root = args.workspace_root or Path.cwd()
    flext = discover_flext_projects(root)
    external = discover_external_projects(root)
    all_projects = discover_all_projects(root)

    if args.format == "makefile":
        if args.kind == "submodule":
            names = [p.name for p in flext]
        elif args.kind == "external":
            names = [p.name for p in external]
        elif args.kind == "all":
            names = [p.name for p in all_projects]
        else:
            names = [p.name for p in all_projects]
        print(" ".join(names))
        return 0

    # Human report
    if args.kind in (None, "all"):
        print(f"=== FLEXT Submodule Projects ({len(flext)}) ===")
        for p in flext:
            print(f"  {p.name}")
        print(f"\n=== External Projects ({len(external)}) ===")
        for p in external:
            print(f"  {p.name} (manual clone required)")
        print(f"\n=== Total: {len(all_projects)} Python projects ===")
    elif args.kind == "submodule":
        print(f"=== FLEXT Submodule Projects ({len(flext)}) ===")
        for p in flext:
            print(f"  {p.name}")
    else:
        print(f"=== External Projects ({len(external)}) ===")
        for p in external:
            print(f"  {p.name} (manual clone required)")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
