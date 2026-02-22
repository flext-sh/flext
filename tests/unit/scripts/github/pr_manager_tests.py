"""Unit tests for scripts.github.pr_manager."""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest


def _load_module(module_name: str, relative_path: str) -> types.ModuleType:
    module_path = Path(__file__).resolve().parents[4] / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_selector_prefers_number() -> None:
    mod = _load_module("pr_manager_selector", "scripts/github/pr_manager.py")
    assert mod._selector("123", "feature/branch") == "123"
    assert mod._selector("", "feature/branch") == "feature/branch"


def test_status_reports_no_open_pr(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    mod = _load_module("pr_manager_status", "scripts/github/pr_manager.py")

    def _fake_capture(command: list[str], _cwd: Path) -> str:
        if command[:3] == ["gh", "pr", "list"]:
            return "[]"
        raise AssertionError(command)

    monkeypatch.setattr(mod, "run_capture", _fake_capture)

    exit_code = mod._print_status(Path("/tmp/repo"), "main", "0.11.0-dev")
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "status=no-open-pr" in output


def test_create_skips_when_existing_open_pr(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    mod = _load_module("pr_manager_create_existing", "scripts/github/pr_manager.py")

    def _fake_open(_repo_root: Path, _head: str) -> dict[str, object] | None:
        return {"url": "https://example.com/pr/1"}

    monkeypatch.setattr(mod, "_open_pr_for_head", _fake_open)

    exit_code = mod._create_pr(
        Path("/tmp/repo"),
        "main",
        "0.11.0-dev",
        "title",
        "body",
        0,
    )
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "status=already-open" in output


def test_open_pr_for_head_parses_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = _load_module("pr_manager_open_payload", "scripts/github/pr_manager.py")
    payload = [{"number": 5, "url": "https://example.com/pr/5"}]

    def _fake_capture(_command: list[str], _cwd: Path) -> str:
        return json.dumps(payload)

    monkeypatch.setattr(mod, "run_capture", _fake_capture)
    pr = mod._open_pr_for_head(Path("/tmp/repo"), "0.11.0-dev")
    assert pr is not None
    assert pr.get("number") == 5


def test_checks_action_nonblocking_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    mod = _load_module("pr_manager_checks_nonblocking", "scripts/github/pr_manager.py")

    def _fake_current_branch(_repo_root: Path) -> str:
        return "0.11.0-dev"

    def _fake_run_stream(_command: list[str], _cwd: Path) -> int:
        return 8

    monkeypatch.setattr(mod, "current_branch", _fake_current_branch)
    monkeypatch.setattr(mod, "_run_stream", _fake_run_stream)
    monkeypatch.setattr(
        mod,
        "_parse_args",
        lambda: mod.argparse.Namespace(
            repo_root=Path(),
            action="checks",
            base="main",
            head="",
            number="",
            title="",
            body="",
            draft=0,
            merge_method="squash",
            auto=0,
            delete_branch=0,
            checks_strict=0,
        ),
    )

    exit_code = mod.main()
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "status=checks-nonblocking" in output


def test_checks_action_strict_mode_returns_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mod = _load_module("pr_manager_checks_strict", "scripts/github/pr_manager.py")

    def _fake_current_branch(_repo_root: Path) -> str:
        return "0.11.0-dev"

    def _fake_run_stream(_command: list[str], _cwd: Path) -> int:
        return 8

    monkeypatch.setattr(mod, "current_branch", _fake_current_branch)
    monkeypatch.setattr(mod, "_run_stream", _fake_run_stream)
    monkeypatch.setattr(
        mod,
        "_parse_args",
        lambda: mod.argparse.Namespace(
            repo_root=Path(),
            action="checks",
            base="main",
            head="",
            number="",
            title="",
            body="",
            draft=0,
            merge_method="squash",
            auto=0,
            delete_branch=0,
            checks_strict=1,
        ),
    )

    assert mod.main() == 8


def test_release_tag_from_head_patterns() -> None:
    mod = _load_module("pr_manager_release_tag", "scripts/github/pr_manager.py")
    assert mod._release_tag_from_head("0.11.0-dev") == "v0.11.0"
    assert mod._release_tag_from_head("release/0.12.3") == "v0.12.3"
    assert mod._release_tag_from_head("feature/x") is None
    assert mod._release_tag_from_head("main") is None


def test_merge_triggers_release_dispatch_when_workspace_repo(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mod = _load_module("pr_manager_merge_release", "scripts/github/pr_manager.py")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    _ = (workflows / "release.yml").write_text("name: release\n", encoding="utf-8")

    run_calls: list[list[str]] = []

    def _fake_run_stream_with_output(command: list[str], _cwd: Path) -> tuple[int, str]:
        run_calls.append(command)
        return 0, ""

    def _fake_run_stream(command: list[str], _cwd: Path) -> int:
        run_calls.append(command)
        if command[:3] == ["gh", "release", "view"]:
            return 1
        return 0

    monkeypatch.setattr(mod, "_run_stream_with_output", _fake_run_stream_with_output)
    monkeypatch.setattr(mod, "_run_stream", _fake_run_stream)

    exit_code = mod._merge_pr(
        repo_root=tmp_path,
        selector="123",
        head="0.11.0-dev",
        method="squash",
        auto=1,
        delete_branch=0,
        release_on_merge=1,
    )

    assert exit_code == 0
    assert run_calls[0] == ["gh", "pr", "merge", "123", "--squash", "--auto"]
    assert run_calls[1] == ["gh", "release", "view", "v0.11.0"]
    assert run_calls[2] == ["gh", "workflow", "run", "release.yml", "-f", "tag=v0.11.0"]
    assert "status=release-dispatched tag=v0.11.0" in capsys.readouterr().out


def test_merge_retries_after_update_branch_on_non_mergeable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    mod = _load_module("pr_manager_merge_retry", "scripts/github/pr_manager.py")

    calls: list[list[str]] = []
    responses = [
        (1, "X Pull request #7 is not mergeable"),
        (0, "updated"),
        (0, "merged"),
    ]

    def _fake_run_stream_with_output(command: list[str], _cwd: Path) -> tuple[int, str]:
        calls.append(command)
        return responses.pop(0)

    def _fake_trigger_release_if_needed(repo_root: Path, head: str) -> None:
        _ = repo_root, head

    monkeypatch.setattr(mod, "_run_stream_with_output", _fake_run_stream_with_output)
    monkeypatch.setattr(
        mod, "_trigger_release_if_needed", _fake_trigger_release_if_needed
    )

    exit_code = mod._merge_pr(
        repo_root=tmp_path,
        selector="7",
        head="0.11.0-dev",
        method="squash",
        auto=0,
        delete_branch=0,
        release_on_merge=0,
    )

    assert exit_code == 0
    assert calls[0] == ["gh", "pr", "merge", "7", "--squash"]
    assert calls[1] == ["gh", "pr", "update-branch", "7", "--rebase"]
    assert calls[2] == ["gh", "pr", "merge", "7", "--squash"]


def test_merge_returns_success_when_no_open_pr_for_head(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    mod = _load_module("pr_manager_merge_no_open", "scripts/github/pr_manager.py")

    def _fake_open_pr_for_head(
        _repo_root: Path, _head: str
    ) -> dict[str, object] | None:
        return None

    def _unexpected_run_stream_with_output(
        _command: list[str], _cwd: Path
    ) -> tuple[int, str]:
        msg = "merge command should not run when PR is absent"
        raise AssertionError(msg)

    monkeypatch.setattr(mod, "_open_pr_for_head", _fake_open_pr_for_head)
    monkeypatch.setattr(
        mod, "_run_stream_with_output", _unexpected_run_stream_with_output
    )

    exit_code = mod._merge_pr(
        repo_root=tmp_path,
        selector="0.11.0-dev",
        head="0.11.0-dev",
        method="squash",
        auto=0,
        delete_branch=0,
        release_on_merge=1,
    )

    assert exit_code == 0
    assert "status=no-open-pr" in capsys.readouterr().out
