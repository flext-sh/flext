"""Unit tests for scripts.maintenance.enforce_python_version."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


def load_module() -> types.ModuleType:
    module_path = (
        Path(__file__).resolve().parents[4]
        / "scripts"
        / "maintenance"
        / "enforce_python_version.py"
    )
    spec = importlib.util.spec_from_file_location("enforce_python_version", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _create_project(root: Path, name: str) -> None:
    project = root / name
    project.mkdir(parents=True)
    (project / ".git").mkdir()
    _ = (project / "Makefile").write_text("all:\n\t@true\n", encoding="utf-8")
    _ = (project / "pyproject.toml").write_text(
        "[project]\nname='demo'\nversion='0.1.0'\n", encoding="utf-8"
    )


def test_discover_projects_includes_external_projects(tmp_path: Path) -> None:
    mod = load_module()
    _create_project(tmp_path, "flext-core")
    _create_project(tmp_path, "algar-oud-mig")
    _ = (tmp_path / ".gitmodules").write_text(
        '[submodule "flext-core"]\n\tpath = flext-core\n\turl = git@github.com:flext-sh/flext-core.git\n',
        encoding="utf-8",
    )

    projects = mod._discover_projects(tmp_path)
    names = [project.name for project in projects]

    assert names == ["algar-oud-mig", "flext-core"]
