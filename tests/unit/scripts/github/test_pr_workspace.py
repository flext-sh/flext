from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from tests.infra import c, t, tm, u


class TestPrWorkspace:
    @staticmethod
    def _args(
        *,
        workspace_root: Path,
        include_root: int,
        fail_fast: int,
        checkpoint: int,
        pr_action: str,
        pr_checks_strict: str,
    ) -> object:
        mod = u.Workspace.Tests.load_module(
            "pr_workspace_args",
            c.Workspace.Tests.MODULE_PR_WORKSPACE,
            anchor_file=Path(__file__),
        )
        return mod.argparse.Namespace(
            workspace_root=workspace_root,
            project=[],
            include_root=include_root,
            branch="0.11.0-dev",
            fail_fast=fail_fast,
            checkpoint=checkpoint,
            pr_action=pr_action,
            pr_base="main",
            pr_head="",
            pr_number="",
            pr_title="",
            pr_body="",
            pr_draft="0",
            pr_merge_method="squash",
            pr_auto="0",
            pr_delete_branch="0",
            pr_checks_strict=pr_checks_strict,
            pr_release_on_merge="1",
        )

    @staticmethod
    def _make_git_dir(path: Path) -> None:
        _ = path.mkdir(parents=True, exist_ok=True)
        _ = (path / ".git").mkdir(exist_ok=True)

    def test_main_runs_projects_and_root(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        mod = u.Workspace.Tests.load_module(
            "pr_workspace_main",
            c.Workspace.Tests.MODULE_PR_WORKSPACE,
            anchor_file=Path(__file__),
        )
        proj_a = tmp_path / "a"
        proj_b = tmp_path / "b"
        for path in (proj_a, proj_b, tmp_path):
            self._make_git_dir(path)

        calls: list[t.Workspace.Tests.RepoCall] = []

        def _resolve_projects(
            _workspace_root: Path,
            _names: list[str],
        ) -> list[SimpleNamespace]:
            return [
                SimpleNamespace(name="a", path=proj_a),
                SimpleNamespace(name="b", path=proj_b),
            ]

        def _checkout_branch(repo: Path, _branch: str) -> None:
            calls.append((c.Workspace.Tests.Calls.CHECKOUT, repo))

        def _checkpoint(repo: Path, _branch: str) -> None:
            calls.append((c.Workspace.Tests.Calls.CHECKPOINT, repo))

        def _run_pr(_repo: Path, _root: Path, _args: t.NormalizedValue) -> int:
            return 0

        monkeypatch.setattr(mod, "resolve_projects", _resolve_projects)
        monkeypatch.setattr(mod, "_checkout_branch", _checkout_branch)
        monkeypatch.setattr(mod, "_checkpoint", _checkpoint)
        monkeypatch.setattr(mod, "_run_pr", _run_pr)
        monkeypatch.setattr(
            mod,
            "_parse_args",
            lambda: self._args(
                workspace_root=tmp_path,
                include_root=1,
                fail_fast=0,
                checkpoint=1,
                pr_action="status",
                pr_checks_strict="0",
            ),
        )

        tm.that(mod.main(), eq=0)
        tm.that(
            [call for call in calls if call[0] == c.Workspace.Tests.Calls.CHECKOUT],
            len=3,
        )
        tm.that(
            [call for call in calls if call[0] == c.Workspace.Tests.Calls.CHECKPOINT],
            len=3,
        )

    def test_main_respects_fail_fast(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        mod = u.Workspace.Tests.load_module(
            "pr_workspace_fail_fast",
            c.Workspace.Tests.MODULE_PR_WORKSPACE,
            anchor_file=Path(__file__),
        )
        proj_a = tmp_path / "a"
        proj_b = tmp_path / "b"
        for path in (proj_a, proj_b):
            self._make_git_dir(path)

        seen: list[Path] = []

        def _resolve_projects(
            _workspace_root: Path,
            _names: list[str],
        ) -> list[SimpleNamespace]:
            return [
                SimpleNamespace(name="a", path=proj_a),
                SimpleNamespace(name="b", path=proj_b),
            ]

        def _run_pr(repo: Path, _root: Path, _args: t.NormalizedValue) -> int:
            seen.append(repo)
            return 2

        monkeypatch.setattr(mod, "resolve_projects", _resolve_projects)
        monkeypatch.setattr(mod, "_checkout_branch", lambda _repo, _branch: None)
        monkeypatch.setattr(mod, "_checkpoint", lambda _repo, _branch: None)
        monkeypatch.setattr(mod, "_run_pr", _run_pr)
        monkeypatch.setattr(
            mod,
            "_parse_args",
            lambda: self._args(
                workspace_root=tmp_path,
                include_root=0,
                fail_fast=1,
                checkpoint=0,
                pr_action="checks",
                pr_checks_strict="1",
            ),
        )

        tm.that(mod.main(), eq=1)
        tm.that(seen, eq=[proj_a])

    def test_run_pr_uses_pr_manager_for_workspace_root(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        mod = u.Workspace.Tests.load_module(
            "pr_workspace_root_command",
            c.Workspace.Tests.MODULE_PR_WORKSPACE,
            anchor_file=Path(__file__),
        )
        workspace = tmp_path / "workspace"
        _ = workspace.mkdir(parents=True)
        commands: list[t.Workspace.Tests.Command] = []

        def _fake_run(
            command: list[str],
            **_kwargs: t.NormalizedValue,
        ) -> SimpleNamespace:
            commands.append(command)
            return SimpleNamespace(returncode=0)

        monkeypatch.setattr(mod.subprocess, "run", _fake_run)
        args = self._args(
            workspace_root=workspace,
            include_root=1,
            fail_fast=0,
            checkpoint=0,
            pr_action="status",
            pr_checks_strict="0",
        )

        tm.that(mod._run_pr(workspace, workspace, args), eq=0)
        tm.that(commands, empty=False)
        tm.that(
            commands[0][:4],
            eq=[
                "python",
                c.Workspace.Tests.PR_MANAGER_COMMAND,
                "--repo-root",
                str(workspace),
            ],
        )

    def test_run_pr_uses_make_for_non_root_repo(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        mod = u.Workspace.Tests.load_module(
            "pr_workspace_project_command",
            c.Workspace.Tests.MODULE_PR_WORKSPACE,
            anchor_file=Path(__file__),
        )
        workspace = tmp_path / "workspace"
        repo = workspace / "flext-core"
        _ = repo.mkdir(parents=True)
        commands: list[t.Workspace.Tests.Command] = []

        def _fake_run(
            command: list[str],
            **_kwargs: t.NormalizedValue,
        ) -> SimpleNamespace:
            commands.append(command)
            return SimpleNamespace(returncode=0)

        monkeypatch.setattr(mod.subprocess, "run", _fake_run)
        args = self._args(
            workspace_root=workspace,
            include_root=0,
            fail_fast=0,
            checkpoint=0,
            pr_action="status",
            pr_checks_strict="0",
        )

        tm.that(mod._run_pr(repo, workspace, args), eq=0)
        tm.that(commands, empty=False)
        tm.that(commands[0][:4], eq=["make", "-C", str(repo), "pr"])
