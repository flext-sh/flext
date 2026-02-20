from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

from _pytest.capture import CaptureFixture
from _pytest.monkeypatch import MonkeyPatch


def load_module() -> Any:
    module_path = (
        Path(__file__).resolve().parents[4] / "scripts" / "maintenance" / "_discover.py"
    )
    spec = importlib.util.spec_from_file_location("_discover", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _create_project(root: Path, name: str) -> None:
    project = root / name
    _ = project.mkdir(parents=True)
    _ = (project / ".git").mkdir()
    _ = (project / "Makefile").write_text("all:\n\t@true\n", encoding="utf-8")
    _ = (project / "pyproject.toml").write_text(
        "[project]\nname='demo'\nversion='0.1.0'\n", encoding="utf-8"
    )


def test_discover_supports_json_output(
    tmp_path: Path, monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    mod = load_module()
    _create_project(tmp_path, "subproj")
    _create_project(tmp_path, "external-proj")
    _ = (tmp_path / ".gitmodules").write_text(
        '[submodule "subproj"]\n\tpath = subproj\n\turl = git@github.com:flext-sh/subproj.git\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        mod.sys,
        "argv",
        [
            "_discover.py",
            "--workspace-root",
            str(tmp_path),
            "--kind",
            "all",
            "--format",
            "json",
        ],
    )

    assert mod.main() == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["count"] == 2
    assert payload["kind"] == "all"
    discovered = {item["name"]: item["kind"] for item in payload["projects"]}
    assert discovered == {"subproj": "submodule", "external-proj": "external"}
