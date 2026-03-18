from __future__ import annotations

from pathlib import Path

import pytest
from tests.infra import c, tm, u


class TestSyncScripts:
    def test_sync_tree_ignores_pycache_and_dot_paths(self, tmp_path: Path) -> None:
        mod = u.Workspace.Tests.load_module(
            "scripts_sync_ignore",
            c.Workspace.Tests.MODULE_SYNC,
            anchor_file=Path(__file__),
        )

        source = tmp_path / "source"
        target = tmp_path / "target"
        _ = (source / "__pycache__").mkdir(parents=True)
        _ = (source / ".hidden").mkdir(parents=True)
        _ = (source / "nested").mkdir(parents=True)
        _ = (source / "__pycache__" / "x.pyc").write_bytes(b"binary")
        _ = (source / ".hidden" / "keep.txt").write_text("skip", encoding="utf-8")
        _ = (source / "nested" / "tool.py").write_text(
            "print('ok')\n", encoding="utf-8"
        )

        changed = mod._sync_tree(source, target, prune=False)
        tm.that(changed, eq=1)
        tm.that((target / "nested" / "tool.py").exists(), eq=True)
        tm.that((target / "__pycache__" / "x.pyc").exists(), eq=False)
        tm.that((target / ".hidden" / "keep.txt").exists(), eq=False)

    def test_main_syncs_scripts_and_libs(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        mod = u.Workspace.Tests.load_module(
            "scripts_sync_main",
            c.Workspace.Tests.MODULE_SYNC,
            anchor_file=Path(__file__),
        )

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
            mod.sys,
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
        tm.that(exit_code, eq=0)
        tm.that((project / "scripts" / "tool.py").exists(), eq=True)
        tm.that((project / "libs" / "versioning.py").exists(), eq=True)
