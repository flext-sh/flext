"""Unit tests for scripts.release.release_shared_and_run."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

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


def test_resolve_projects_uses_auto_discovery(monkeypatch: pytest.MonkeyPatch) -> None:
    shared = _load_module("release_shared", "scripts/release/shared.py")

    def _fake_resolve(_root: Path, _names: list[str]) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(name="external-tool"),
            SimpleNamespace(name="flext-api"),
        ]

    monkeypatch.setattr(shared, "_resolve_projects", _fake_resolve)

    projects = shared.resolve_projects(Path("/tmp/ws"), [])
    assert [project.name for project in projects] == ["external-tool", "flext-api"]


def test_resolve_projects_rejects_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    shared = _load_module("release_shared_unknown", "scripts/release/shared.py")

    def _fake_resolve(_root: Path, _names: list[str]) -> list[object]:
        msg = "unknown projects: missing-project"
        raise RuntimeError(msg)

    monkeypatch.setattr(shared, "_resolve_projects", _fake_resolve)

    with pytest.raises(RuntimeError, match="unknown release projects"):
        _ = shared.resolve_projects(Path("/tmp/ws"), ["missing-project"])


def test_current_version_reads_project_table(tmp_path: Path) -> None:
    run_mod = _load_module("release_run", "scripts/release/run.py")
    pyproject = tmp_path / "pyproject.toml"
    _ = pyproject.write_text(
        """[tool.sample]
version = "999.999.999"

[project]
name = "demo"
version = "0.10.0-dev"
""",
        encoding="utf-8",
    )

    assert run_mod._current_version(tmp_path) == "0.10.0"


def test_phase_version_passes_dev_suffix_flag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    run_mod = _load_module("release_run_phase_version_dev", "scripts/release/run.py")
    recorded: list[list[str]] = []

    def _fake_run_checked(command: list[str], cwd: Path | None = None) -> None:
        _ = cwd
        recorded.append(command)

    monkeypatch.setattr(run_mod, "run_checked", _fake_run_checked)

    run_mod._phase_version(
        root=tmp_path,
        version="0.12.0",
        dry_run=False,
        project_names=["flext-core"],
        dev_suffix=True,
    )

    assert recorded
    assert "--dev-suffix" in recorded[0]
    assert "1" in recorded[0]


def test_phase_next_dev_bumps_and_appends_dev(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    run_mod = _load_module("release_run_next_dev", "scripts/release/run.py")
    recorded: list[list[str]] = []

    def _fake_phase_version(
        root: Path,
        version: str,
        dry_run: bool,
        project_names: list[str],
        dev_suffix: bool,
    ) -> None:
        _ = root, dry_run, project_names
        recorded.append([version, "dev" if dev_suffix else "nodev"])

    monkeypatch.setattr(run_mod, "_phase_version", _fake_phase_version)

    next_version = run_mod._phase_next_dev(
        root=tmp_path,
        version="0.11.0",
        project_names=["flext-core"],
        bump="minor",
    )

    assert next_version == "0.12.0"
    assert recorded == [["0.12.0", "dev"]]
