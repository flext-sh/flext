from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest


def _load_module(module_name: str, relative_path: str) -> Any:
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

    monkeypatch.setattr(mod, "_run_capture", _fake_capture)

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

    monkeypatch.setattr(mod, "_run_capture", _fake_capture)
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

    monkeypatch.setattr(mod, "_current_branch", _fake_current_branch)
    monkeypatch.setattr(mod, "_run_stream", _fake_run_stream)
    monkeypatch.setattr(
        mod,
        "_parse_args",
        lambda: mod.argparse.Namespace(
            repo_root=Path("."),
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

    monkeypatch.setattr(mod, "_current_branch", _fake_current_branch)
    monkeypatch.setattr(mod, "_run_stream", _fake_run_stream)
    monkeypatch.setattr(
        mod,
        "_parse_args",
        lambda: mod.argparse.Namespace(
            repo_root=Path("."),
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
