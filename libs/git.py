from __future__ import annotations

from pathlib import Path

from libs.subprocess import run_capture


def current_branch(repo_root: Path) -> str:
    return run_capture(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root)


def tag_exists(repo_root: Path, tag: str) -> bool:
    value = run_capture(["git", "tag", "-l", tag], cwd=repo_root)
    return value.strip() == tag
