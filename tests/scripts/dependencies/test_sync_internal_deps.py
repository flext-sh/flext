from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

from _pytest.monkeypatch import MonkeyPatch


def load_module() -> Any:
    module_path = (
        Path(__file__).resolve().parents[3]
        / "scripts"
        / "dependencies"
        / "sync_internal_deps.py"
    )
    spec = importlib.util.spec_from_file_location("sync_internal_deps", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git_fail_result() -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["git"], returncode=1, stdout="", stderr="")


def _git_fail(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
    return _git_fail_result()


def _owner_flext_sh(_root: Path) -> str:
    return "flext-sh"


def _ref_main(_root: Path) -> str:
    return "main"


def _capture_checkout(
    captured: list[tuple[Path, str, str]],
) -> Any:
    def _inner(dep_path: Path, repo_url: str, ref_name: str) -> None:
        captured.append((dep_path, repo_url, ref_name))

    return _inner


def test_workspace_mode_uses_explicit_workspace_env(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    mod = load_module()
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "nested" / "project"
    _ = project_root.mkdir(parents=True)

    monkeypatch.setenv("FLEXT_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.delenv("FLEXT_STANDALONE", raising=False)
    monkeypatch.setattr(mod, "_run_git", _git_fail)

    workspace_mode, resolved_root = mod._is_workspace_mode(project_root)

    assert workspace_mode is True
    assert resolved_root == workspace_root


def test_workspace_mode_finds_parent_gitmodules(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    mod = load_module()
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "nested" / "project"
    _ = project_root.mkdir(parents=True)
    _ = (workspace_root / ".gitmodules").write_text("", encoding="utf-8")

    monkeypatch.delenv("FLEXT_WORKSPACE_ROOT", raising=False)
    monkeypatch.delenv("FLEXT_STANDALONE", raising=False)
    monkeypatch.setattr(mod, "_run_git", _git_fail)

    workspace_mode, resolved_root = mod._is_workspace_mode(project_root)

    assert workspace_mode is True
    assert resolved_root == workspace_root


def test_standalone_fallback_synthesizes_repo_urls(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    mod = load_module()
    project_root = tmp_path / "flext-cli"
    _ = project_root.mkdir(parents=True)
    _ = (project_root / "pyproject.toml").write_text(
        """
[tool.poetry]
name = "flext-cli"
version = "0.1.0"

[tool.poetry.dependencies]
python = ">=3.13"
flext-core = { path = ".flext-deps/flext-core" }
""".strip()
        + "\n",
        encoding="utf-8",
    )

    captured: list[tuple[Path, str, str]] = []

    monkeypatch.setenv("FLEXT_STANDALONE", "1")
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setattr(mod, "_infer_owner_from_origin", _owner_flext_sh)
    monkeypatch.setattr(mod, "_resolve_ref", _ref_main)
    monkeypatch.setattr(mod, "_ensure_checkout", _capture_checkout(captured))
    monkeypatch.setattr(
        mod.sys,
        "argv",
        ["sync_internal_deps.py", "--project-root", str(project_root)],
    )

    assert mod._main() == 0
    assert len(captured) == 1
    dep_path, repo_url, ref_name = captured[0]
    assert dep_path == project_root / ".flext-deps" / "flext-core"
    assert repo_url == "git@github.com:flext-sh/flext-core.git"
    assert ref_name == "main"
