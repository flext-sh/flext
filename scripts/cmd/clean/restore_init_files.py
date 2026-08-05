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

from flext_cli import p, r, u as cli_u
from flext_infra import m, u as infra_u
from scripts.dispatch import Dispatch


def _is_git_repo(path: Path) -> bool:
    return infra_u.Infra.git_show_toplevel(
        m.Infra.GitRepoRequest(repo_root=path)
    ).success


def _changed_init_files(repo: Path) -> list[str]:
    """List ``__init__.py`` files that differ from HEAD (staged or unstaged)."""
    status = infra_u.Infra.git_status(m.Infra.GitStatusRequest(repo_root=repo))
    if status.failure:
        return []
    changed: set[str] = set()
    for line in status.value.porcelain.splitlines():
        path_text = line.split(" ", 1)[-1].strip()
        if path_text.endswith("__init__.py"):
            changed.add(path_text)
    return sorted(changed)


def _restore_files(repo: Path, files: list[str]) -> p.Result[bool]:
    restored = infra_u.Infra.git_restore_paths(
        m.Infra.GitCheckoutPathsRequest(repo_root=repo, paths=files)
    )
    if restored.failure:
        return r[bool].fail(restored.error or "git restore failed")
    return r[bool].ok(True)


def _validate_imports(workspace_root: Path) -> p.Result[bool]:
    env = cli_u.Cli.process_env(
        overrides={
            "PYTHONPATH": ":".join(
                str(workspace_root / proj / "src")
                for proj in ("flext-core", "flext-cli", "flext-tests", "flext-infra")
            )
        }
    )
    return cli_u.Cli.run_checked(
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
        cli_u.Cli.process_env().get("WORKSPACE_ROOT", str(Path.cwd()))
    ).resolve()
    if Dispatch.surface_validation_enabled():
        return 0
    if not Dispatch.env_enabled("APPLY"):
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
            skipped += 1
            continue

        init_files = _changed_init_files(repo)
        if not init_files:
            skipped += 1
            continue

        restore_result = _restore_files(repo, init_files)
        if restore_result.failure:
            failed += 1
            continue

        restored += 1

    if failed:
        return 1

    validation = _validate_imports(workspace_root)
    if validation.failure:
        return 1
    return 0


if __name__ == "__main__":
    Dispatch.promoted_main(__file__, run)
