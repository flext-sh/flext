from __future__ import annotations

from pathlib import Path


def reports_root(workspace_root: Path) -> Path:
    return workspace_root / ".reports"


def ensure_report_dir(workspace_root: Path, *parts: str) -> Path:
    path = reports_root(workspace_root).joinpath(*parts)
    path.mkdir(parents=True, exist_ok=True)
    return path
