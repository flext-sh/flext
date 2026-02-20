from __future__ import annotations

import importlib.util
import json
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
    payload = {
        "projects": [
            {"name": "flext-api", "path": "/tmp/ws/flext-api", "kind": "submodule"},
            {
                "name": "external-tool",
                "path": "/tmp/ws/external-tool",
                "kind": "external",
            },
        ]
    }

    def _fake_run(*_args: object, **_kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(shared.subprocess, "run", _fake_run)

    projects = shared.resolve_projects(Path("/tmp/ws"), [])
    assert [project.name for project in projects] == ["external-tool", "flext-api"]


def test_resolve_projects_rejects_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    shared = _load_module("release_shared_unknown", "scripts/release/shared.py")
    payload = {
        "projects": [
            {"name": "flext-api", "path": "/tmp/ws/flext-api", "kind": "submodule"},
        ]
    }

    def _fake_run(*_args: object, **_kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(shared.subprocess, "run", _fake_run)

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
