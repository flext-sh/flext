from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


def _load_module(module_name: str, relative_path: str):
    module_path = Path(__file__).resolve().parents[3] / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_main_runs_projects_and_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    mod = _load_module("pr_workspace_main", "scripts/github/pr_workspace.py")

    proj_a = tmp_path / "a"
    proj_b = tmp_path / "b"
    for path in (proj_a, proj_b, tmp_path):
        _ = path.mkdir(parents=True, exist_ok=True)
        _ = (path / ".git").mkdir(exist_ok=True)

    calls: list[tuple[str, Path]] = []

    def _resolve_projects(
        _workspace_root: Path, _names: list[str]
    ) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(name="a", path=proj_a),
            SimpleNamespace(name="b", path=proj_b),
        ]

    def _checkout_branch(repo: Path, _branch: str) -> None:
        calls.append(("co", repo))

    def _checkpoint(repo: Path, _branch: str) -> None:
        calls.append(("cp", repo))

    def _run_pr(_repo: Path, _root: Path, _args) -> int:
        return 0

    monkeypatch.setattr(mod, "resolve_projects", _resolve_projects)
    monkeypatch.setattr(mod, "_checkout_branch", _checkout_branch)
    monkeypatch.setattr(mod, "_checkpoint", _checkpoint)
    monkeypatch.setattr(mod, "_run_pr", _run_pr)
    monkeypatch.setattr(
        mod,
        "_parse_args",
        lambda: mod.argparse.Namespace(
            workspace_root=tmp_path,
            project=[],
            include_root=1,
            branch="0.11.0-dev",
            fail_fast=0,
            checkpoint=1,
            pr_action="status",
            pr_base="main",
            pr_head="",
            pr_number="",
            pr_title="",
            pr_body="",
            pr_draft="0",
            pr_merge_method="squash",
            pr_auto="0",
            pr_delete_branch="0",
            pr_checks_strict="0",
            pr_release_on_merge="1",
        ),
    )

    assert mod.main() == 0
    assert len([call for call in calls if call[0] == "co"]) == 3
    assert len([call for call in calls if call[0] == "cp"]) == 3


def test_main_respects_fail_fast(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    mod = _load_module("pr_workspace_fail_fast", "scripts/github/pr_workspace.py")

    proj_a = tmp_path / "a"
    proj_b = tmp_path / "b"
    for path in (proj_a, proj_b):
        _ = path.mkdir(parents=True, exist_ok=True)
        _ = (path / ".git").mkdir(exist_ok=True)

    seen: list[Path] = []

    def _resolve_projects(
        _workspace_root: Path, _names: list[str]
    ) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(name="a", path=proj_a),
            SimpleNamespace(name="b", path=proj_b),
        ]

    def _checkout_branch(_repo: Path, _branch: str) -> None:
        return None

    def _checkpoint(_repo: Path, _branch: str) -> None:
        return None

    monkeypatch.setattr(mod, "resolve_projects", _resolve_projects)
    monkeypatch.setattr(mod, "_checkout_branch", _checkout_branch)
    monkeypatch.setattr(mod, "_checkpoint", _checkpoint)

    def _run_pr(repo: Path, _root: Path, _args) -> int:
        seen.append(repo)
        return 2

    monkeypatch.setattr(mod, "_run_pr", _run_pr)
    monkeypatch.setattr(
        mod,
        "_parse_args",
        lambda: mod.argparse.Namespace(
            workspace_root=tmp_path,
            project=[],
            include_root=0,
            branch="0.11.0-dev",
            fail_fast=1,
            checkpoint=0,
            pr_action="checks",
            pr_base="main",
            pr_head="",
            pr_number="",
            pr_title="",
            pr_body="",
            pr_draft="0",
            pr_merge_method="squash",
            pr_auto="0",
            pr_delete_branch="0",
            pr_checks_strict="1",
            pr_release_on_merge="1",
        ),
    )

    assert mod.main() == 1
    assert seen == [proj_a]


def test_run_pr_uses_pr_manager_for_workspace_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    mod = _load_module("pr_workspace_root_command", "scripts/github/pr_workspace.py")
    workspace = tmp_path / "workspace"
    _ = workspace.mkdir(parents=True)

    commands: list[list[str]] = []

    def _fake_run(command: list[str], **_kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(mod.subprocess, "run", _fake_run)

    args = mod.argparse.Namespace(
        pr_action="status",
        pr_base="main",
        pr_head="",
        pr_number="",
        pr_title="",
        pr_body="",
        pr_draft="0",
        pr_merge_method="squash",
        pr_auto="0",
        pr_delete_branch="0",
        pr_checks_strict="0",
        pr_release_on_merge="1",
    )

    exit_code = mod._run_pr(workspace, workspace, args)
    assert exit_code == 0
    assert commands
    assert commands[0][:4] == [
        "python",
        "scripts/github/pr_manager.py",
        "--repo-root",
        str(workspace),
    ]


def test_run_pr_uses_make_for_non_root_repo(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    mod = _load_module("pr_workspace_project_command", "scripts/github/pr_workspace.py")
    workspace = tmp_path / "workspace"
    repo = workspace / "flext-core"
    _ = repo.mkdir(parents=True)

    commands: list[list[str]] = []

    def _fake_run(command: list[str], **_kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(mod.subprocess, "run", _fake_run)

    args = mod.argparse.Namespace(
        pr_action="status",
        pr_base="main",
        pr_head="",
        pr_number="",
        pr_title="",
        pr_body="",
        pr_draft="0",
        pr_merge_method="squash",
        pr_auto="0",
        pr_delete_branch="0",
        pr_checks_strict="0",
        pr_release_on_merge="1",
    )

    exit_code = mod._run_pr(repo, workspace, args)
    assert exit_code == 0
    assert commands
    assert commands[0][:4] == ["make", "-C", str(repo), "pr"]
