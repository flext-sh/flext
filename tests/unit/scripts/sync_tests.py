from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_module(module_name: str, relative_path: str):
    module_path = Path(__file__).resolve().parents[3] / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_sync_tree_ignores_pycache_and_dot_paths(tmp_path: Path) -> None:
    mod = _load_module("scripts_sync_ignore", "scripts/sync.py")

    source = tmp_path / "source"
    target = tmp_path / "target"
    _ = (source / "__pycache__").mkdir(parents=True)
    _ = (source / ".hidden").mkdir(parents=True)
    _ = (source / "nested").mkdir(parents=True)
    _ = (source / "__pycache__" / "x.pyc").write_bytes(b"binary")
    _ = (source / ".hidden" / "keep.txt").write_text("skip", encoding="utf-8")
    _ = (source / "nested" / "tool.py").write_text("print('ok')\n", encoding="utf-8")

    changed = mod._sync_tree(source, target, prune=False)
    assert changed == 1
    assert (target / "nested" / "tool.py").exists()
    assert not (target / "__pycache__" / "x.pyc").exists()
    assert not (target / ".hidden" / "keep.txt").exists()


def test_main_syncs_scripts_and_libs(tmp_path: Path, monkeypatch) -> None:
    mod = _load_module("scripts_sync_main", "scripts/sync.py")

    canonical = tmp_path / "canonical"
    project = tmp_path / "project"
    _ = (canonical / "scripts").mkdir(parents=True)
    _ = (canonical / "libs").mkdir(parents=True)
    _ = (project / "scripts").mkdir(parents=True)
    _ = (canonical / "base.mk").write_text("BASE\n", encoding="utf-8")
    _ = (canonical / "scripts" / "tool.py").write_text(
        "print('sync')\n", encoding="utf-8"
    )
    _ = (canonical / "libs" / "versioning.py").write_text(
        "VALUE = 'v'\n", encoding="utf-8"
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sync.py",
            "--project-root",
            str(project),
            "--canonical-root",
            str(canonical),
        ],
    )

    exit_code = mod.main()
    assert exit_code == 0
    assert (project / "scripts" / "tool.py").exists()
    assert (project / "libs" / "versioning.py").exists()
