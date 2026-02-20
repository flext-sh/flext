from __future__ import annotations

from pathlib import Path


def workspace_root(path: str | Path = ".") -> Path:
    return Path(path).resolve()


def repo_root_from_script(script_file: str | Path) -> Path:
    return Path(script_file).resolve().parents[1]
