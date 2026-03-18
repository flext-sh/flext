from __future__ import annotations

from pathlib import Path

from flext_tests.matchers import FlextTestsMatchers as tm

from ...infra import c, u


class TestSyncScripts:
    def test_sync_generates_basemk_and_gitignore(self, tmp_path: Path) -> None:
        mod = u.Workspace.Tests.load_module(
            "workspace_sync_service",
            c.Workspace.Tests.MODULE_SYNC,
            anchor_file=Path(__file__),
        )

        canonical = tmp_path / "canonical"
        project = tmp_path / "project"
        _ = canonical.mkdir(parents=True)
        _ = project.mkdir(parents=True)
        _ = (canonical / "base.mk").write_text("BASE = 1\n", encoding="utf-8")

         service = mod.FlextInfraSyncService(canonical_root=canonical)
         result = service.sync(workspace_root=project)
         tm.ok(result)
         sync_result = result.value

         tm.that(sync_result.files_changed, gte=1)
        tm.that((project / "base.mk").exists(), eq=True)
        tm.that((project / ".gitignore").exists(), eq=True)

    def test_sync_is_idempotent_on_second_run(self, tmp_path: Path) -> None:
        mod = u.Workspace.Tests.load_module(
            "workspace_sync_idempotent",
            c.Workspace.Tests.MODULE_SYNC,
            anchor_file=Path(__file__),
        )

        canonical = tmp_path / "canonical"
        project = tmp_path / "project"
        _ = canonical.mkdir(parents=True)
        _ = project.mkdir(parents=True)
        _ = (canonical / "base.mk").write_text("BASE = 1\n", encoding="utf-8")

        service = mod.FlextInfraSyncService(canonical_root=canonical)
        _ = tm.ok(service.sync(workspace_root=project))
        second = tm.ok(service.sync(workspace_root=project))

        tm.that(second.files_changed, eq=0)
