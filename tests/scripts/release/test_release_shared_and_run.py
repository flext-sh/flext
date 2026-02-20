from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest


def _load_module(module_name: str, relative_path: str) -> Any:
    module_path = Path(__file__).resolve().parents[3] / relative_path
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
        raise RuntimeError("unknown projects: missing-project")

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
