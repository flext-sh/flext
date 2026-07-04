#!/usr/bin/env python3
"""Restore modified __init__.py files across workspace git repositories.

Equivalent to the legacy ``restore_init_files.sh`` helper. Finds every git
repository under the workspace, lists staged and unstaged ``__init__.py``
changes, restores them, then verifies that the core packages still import.
"""
# /// flext-command
# verb = "clean"
# what = "restore_init_files"
# domain = "workspace"
# summary = "Restore modified __init__.py files"
# description = "Restores staged and unstaged __init__.py changes in workspace git repositories and validates core imports."
# example = "make clean WHAT=restore_init_files APPLY=Y"
# mutates = true
# aliases = []
# params = [
#   { name = "APPLY", help = "Must be Y to restore files", required = true, default = "N", choices = ["Y", "N"] }
# ]
# rules = ["workspace-bootstrap"]
# ///

from __future__ import annotations

import sys
from pathlib import Path

from scripts.dispatch import Dispatch

from flext_cli import p, u


def _is_git_repo(path: Path) -> bool:
    return u.Cli.run_checked(
        ["git", "rev-parse", "--git-dir"],
        cwd=path,
    ).unwrap_or(False)


def _changed_init_files(repo: Path) -> list[str]:
    changed: set[str] = set()
    for flag in ("--cached", None):
        cmd = ["git", "diff", "--name-only"]
        if flag:
            cmd.append(flag)
        cmd.extend(("--", "**/__init__.py"))
        result = u.Cli.capture(cmd, cwd=repo)
        if result.success:
            changed.update(
                line.strip() for line in result.value.splitlines() if line.strip()
            )
    return sorted(changed)


def _restore_files(repo: Path, files: list[str]) -> p.Result[bool]:
    return u.Cli.run_checked(
        ["git", "restore", "--staged", "--worktree", "--", *files],
        cwd=repo,
    )


def _validate_imports(workspace_root: Path) -> p.Result[bool]:
    env = u.Cli.process_env(
        overrides={
            "PYTHONPATH": ":".join(
                str(workspace_root / proj / "src")
                for proj in (
                    "flext-core",
                    "flext-cli",
                    "flext-tests",
                    "flext-infra",
                )
            ),
        },
    )
    return u.Cli.run_checked(
        [
            sys.executable,
            "-c",
            "import flext_infra, flext_core, flext_cli, flext_tests; print('ok')",
        ],
        cwd=workspace_root,
        env=env,
    )


def run() -> int:
    """Run the restore workflow."""
    workspace_root = Path(
        u.Cli.process_env().get("WORKSPACE_ROOT", str(Path.cwd())),
    ).resolve()
    if Dispatch.surface_validation_enabled():
        print("SURFACE-VALIDATE: python -m scripts.cmd.clean.restore_init_files")
        return 0
    if not Dispatch.env_enabled("APPLY"):
        print("DRY RUN: set APPLY=Y to restore __init__.py files")
        return 0

    repos = [workspace_root] + [
        path
        for path in workspace_root.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ]

    total = restored = skipped = failed = 0
    for repo in repos:
        total += 1
        if not _is_git_repo(repo):
            print(f"SKIP  {repo} (not a git repository)")
            skipped += 1
            continue

        init_files = _changed_init_files(repo)
        if not init_files:
            print(f"OK    {repo} (no __init__.py changes)")
            skipped += 1
            continue

        print(f"WORK  {repo}: {len(init_files)} file(s)")
        restore_result = _restore_files(repo, init_files)
        if restore_result.failure:
            print(f"FAIL  {repo} ({restore_result.error})")
            failed += 1
            continue

        print(f"DONE  {repo}")
        restored += 1

    print(
        f"SUMMARY total={total} restored={restored} skipped={skipped} failed={failed}",
    )
    if failed:
        return 1

    print("VALIDATING core imports...")
    validation = _validate_imports(workspace_root)
    if validation.failure:
        print(f"FAIL  import validation ({validation.error})")
        return 1
    print("OK    core imports")
    return 0


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, run)
