from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from flext_core import r
from flext_tests import tm

from ....infra.constants import c
from ....infra.typings import t
from ....infra.utilities import u


class TestPrWorkspace:
    @staticmethod
    def _pr_args() -> Mapping[str, str]:
        return {
            "action": "status",
            "base": "main",
            "draft": "0",
            "merge_method": "squash",
            "auto": "0",
            "delete_branch": "0",
            "checks_strict": "0",
            "release_on_merge": "1",
        }

    def test_build_root_command_uses_python_module(self, tmp_path: Path) -> None:
        mod = u.Workspace.Tests.load_module(
            "pr_workspace_root_cmd",
            c.Workspace.Tests.MODULE_PR_WORKSPACE,
            anchor_file=Path(__file__),
        )
        repo = tmp_path / "workspace"
        _ = repo.mkdir(parents=True)

        command = mod.FlextInfraPrWorkspaceManager._build_root_command(
            repo,
            self._pr_args(),
        )

        tm.that(
            command[:5],
            eq=[
                "python",
                "-m",
                c.Workspace.Tests.PR_MANAGER_MODULE,
                "--repo-root",
                str(repo),
            ],
        )

    def test_build_subproject_command_uses_make(self, tmp_path: Path) -> None:
        mod = u.Workspace.Tests.load_module(
            "pr_workspace_subproject_cmd",
            c.Workspace.Tests.MODULE_PR_WORKSPACE,
            anchor_file=Path(__file__),
        )
        repo = tmp_path / "flext-core"
        _ = repo.mkdir(parents=True)

        command = mod.FlextInfraPrWorkspaceManager._build_subproject_command(
            repo,
            self._pr_args(),
        )

        tm.that(command[:4], eq=["make", "-C", str(repo), "pr"])

    def test_run_pr_uses_root_command_for_workspace(self, tmp_path: Path) -> None:
        mod = u.Workspace.Tests.load_module(
            "pr_workspace_run_root",
            c.Workspace.Tests.MODULE_PR_WORKSPACE,
            anchor_file=Path(__file__),
        )
        workspace = tmp_path / "workspace"
        _ = workspace.mkdir(parents=True)
        commands: Sequence[t.Workspace.Tests.Command] = []

        class RunnerStub:
            def run_to_file(self, command: Sequence[str], _log_path: Path) -> r[int]:
                commands.append(command)
                return r[int].ok(0)

        class ReportingStub:
            def get_report_dir(self, _root: Path, _scope: str, _verb: str) -> Path:
                report_dir = tmp_path / "reports"
                _ = report_dir.mkdir(parents=True, exist_ok=True)
                return report_dir

        manager = mod.FlextInfraPrWorkspaceManager(
            runner=RunnerStub(),
            selector=None,
            reporting=ReportingStub(),
        )
        result = manager.run_pr(workspace, workspace, self._pr_args())
        tm.ok(result)
        run_data = result.value

        tm.that(run_data.exit_code, eq=0)
        tm.that(commands, empty=False)
        tm.that(
            commands[0][:5],
            eq=[
                "python",
                "-m",
                c.Workspace.Tests.PR_MANAGER_MODULE,
                "--repo-root",
                str(workspace),
            ],
        )

    def test_run_pr_uses_make_command_for_subproject(self, tmp_path: Path) -> None:
        mod = u.Workspace.Tests.load_module(
            "pr_workspace_run_subproject",
            c.Workspace.Tests.MODULE_PR_WORKSPACE,
            anchor_file=Path(__file__),
        )
        workspace = tmp_path / "workspace"
        repo = workspace / "flext-core"
        _ = repo.mkdir(parents=True)
        commands: Sequence[t.Workspace.Tests.Command] = []

        class RunnerStub:
            def run_to_file(self, command: Sequence[str], _log_path: Path) -> r[int]:
                commands.append(command)
                return r[int].ok(0)

        class ReportingStub:
            def get_report_dir(self, _root: Path, _scope: str, _verb: str) -> Path:
                report_dir = tmp_path / "reports"
                _ = report_dir.mkdir(parents=True, exist_ok=True)
                return report_dir

        manager = mod.FlextInfraPrWorkspaceManager(
            runner=RunnerStub(),
            selector=None,
            reporting=ReportingStub(),
        )
        result = manager.run_pr(repo, workspace, self._pr_args())
        tm.ok(result)
        run_data = result.value

        tm.that(run_data.exit_code, eq=0)
        tm.that(commands, empty=False)
        tm.that(commands[0][:4], eq=["make", "-C", str(repo), "pr"])
