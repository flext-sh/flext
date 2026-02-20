from __future__ import annotations

from pathlib import Path

from libs.discovery import ProjectInfo, discover_projects


def filter_projects(projects: list[ProjectInfo], kind: str) -> list[ProjectInfo]:
    if kind == "all":
        return list(projects)
    return [project for project in projects if project.kind == kind]


def resolve_projects(workspace_root: Path, names: list[str]) -> list[ProjectInfo]:
    projects = discover_projects(workspace_root)
    if not names:
        return sorted(projects, key=lambda project: project.name)

    by_name = {project.name: project for project in projects}
    missing = [name for name in names if name not in by_name]
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise RuntimeError(f"unknown projects: {missing_text}")

    resolved = [by_name[name] for name in names]
    return sorted(resolved, key=lambda project: project.name)
