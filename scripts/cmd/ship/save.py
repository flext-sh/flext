#!/usr/bin/env python3
"""Commit all changes in selected workspace projects and root.

Equivalent to the legacy ``commit_submodules.sh`` / ``_save`` Makefile target.
Discovers selected git repositories, stages modified/deleted/untracked files,
and creates commits with the provided message.
"""
# /// flext-command
# verb = "ship"
# what = "save"
# domain = "release"
# summary = "Commit all changes in selected projects"
# description = "Stages and commits modified, deleted, and untracked files in selected workspace git repositories and root."
# example = "make ship WHAT=save APPLY=Y MESSAGE='chore: update'"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to commit changes", required = true, default = "N", choices = ["Y", "N"] },
#   { name = "MESSAGE", help = "Commit message", required = true, default = "" }
# ]
# rules = ["release"]
# ///

from __future__ import annotations

from pathlib import Path

from flext_cli import p, r, u as cli_u
from flext_infra import m, u as infra_u
from scripts.dispatch import Dispatch


def _selected_projects(workspace_root: Path) -> list[str]:
    """Return the project list from env or discover git repositories."""
    env = cli_u.Cli.process_env()
    if project := env.get("PROJECT", "").strip():
        return [project]
    if projects := env.get("PROJECTS", "").strip():
        return projects.split()
    return sorted(
        path.name
        for path in workspace_root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and (path / ".git").exists()
    )


def _is_git_repo(path: Path) -> bool:
    return infra_u.Infra.git_show_toplevel(
        m.Infra.GitRepoRequest(repo_root=path)
    ).success


def _has_changes(repo: Path) -> bool:
    result = infra_u.Infra.git_status(m.Infra.GitStatusRequest(repo_root=repo))
    return result.success and result.value.dirty


def _stage_and_commit(repo: Path, message: str) -> p.Result[bool]:
    """Stage modified/deleted/untracked files and commit via typed Git facade."""
    status = infra_u.Infra.git_status(m.Infra.GitStatusRequest(repo_root=repo))
    if status.failure:
        return r[bool].fail(status.error or "failed to read git status")
    porcelain = status.value.porcelain
    files = [line.split(" ", 1)[-1] for line in porcelain.splitlines() if line.strip()]
    if not files:
        return r[bool].ok(True)

    added = infra_u.Infra.git_add_paths(
        m.Infra.GitPathsRequest(repo_root=repo, paths=files)
    )
    if added.failure:
        return r[bool].fail(added.error or "git add failed")
    committed = infra_u.Infra.git_commit(
        m.Infra.GitCommitRequest(repo_root=repo, message=message)
    )
    if committed.failure:
        return r[bool].fail(committed.error or "git commit failed")
    return r[bool].ok(True)


def run() -> int:
    """Run the save (commit) workflow."""
    env = cli_u.Cli.process_env()
    workspace_root = Path(env.get("WORKSPACE_ROOT", str(Path.cwd()))).resolve()
    message = env.get("MESSAGE", "").strip()

    if not message:
        return 1

    if Dispatch.surface_validation_enabled():
        return 0

    if not Dispatch.env_enabled("APPLY"):
        return 0

    projects = _selected_projects(workspace_root)
    committed = skipped = failed = 0

    for name in projects:
        repo = workspace_root / name
        if not _is_git_repo(repo):
            continue
        if not _has_changes(repo):
            skipped += 1
            continue

        result = _stage_and_commit(repo, message)
        if result.success:
            committed += 1
        else:
            failed += 1

    if _is_git_repo(workspace_root) and _has_changes(workspace_root):
        result = _stage_and_commit(workspace_root, message)
        if result.success:
            committed += 1
        else:
            failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, run)
