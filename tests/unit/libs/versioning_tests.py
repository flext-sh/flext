"""FLEXT infra test helpers for versioning_tests."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from flext_tests import tm

from tests.infra.constants import c
from tests.infra.utilities import u

if TYPE_CHECKING:
    import pytest


class TestVersioning:
    def test_parse_and_bump_semver(self) -> None:
        mod = u.Workspace.Tests.load_module(
            "libs_versioning_semver",
            c.Workspace.Tests.MODULE_VERSIONING,
            anchor_file=Path(__file__),
        )
        tm.that(mod.parse_semver("1.2.3"), eq=(1, 2, 3))
        tm.that(mod.bump_version("1.2.3", "patch"), eq="1.2.4")
        tm.that(mod.bump_version("1.2.3", "minor"), eq="1.3.0")
        tm.that(mod.bump_version("1.2.3", "major"), eq="2.0.0")

    def test_release_tag_from_branch_patterns(self) -> None:
        mod = u.Workspace.Tests.load_module(
            "libs_versioning_release",
            c.Workspace.Tests.MODULE_VERSIONING,
            anchor_file=Path(__file__),
        )
        tm.that(mod.release_tag_from_branch("0.11.0-dev"), eq="v0.11.0")
        tm.that(mod.release_tag_from_branch("release/0.12.3"), eq="v0.12.3")
        tm.that(mod.release_tag_from_branch("feature/abc"), none=True)

    def test_replace_project_version_updates_only_project_table(self) -> None:
        mod = u.Workspace.Tests.load_module(
            "libs_versioning_replace",
            c.Workspace.Tests.MODULE_VERSIONING,
            anchor_file=Path(__file__),
        )
        content = """
[project]
name = "demo"
version = "0.11.0-dev"

[tool.poetry.dependencies]
python = ">=3.13,<4.0"
flext-core = "0.11.0-dev"
""".strip()
        updated, did_change = mod.replace_project_version(content, "0.11.0")
        tm.that(did_change, eq=True)
        tm.that(updated, has='version = "0.11.0"')
        tm.that(updated, has='flext-core = "0.11.0-dev"')

    def test_current_workspace_version_reads_project_version(
        self, tmp_path: Path
    ) -> None:
        mod = u.Workspace.Tests.load_module(
            "libs_versioning_current",
            c.Workspace.Tests.MODULE_VERSIONING,
            anchor_file=Path(__file__),
        )
        pyproject = tmp_path / "pyproject.toml"
        _ = pyproject.write_text(
            """
[project]
name = "demo"
version = "0.10.0-dev"
""".strip(),
            encoding="utf-8",
        )
        tm.that(mod.current_workspace_version(tmp_path), eq="0.10.0")

    def test_libs_package_exports_versioning_helpers(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        root = Path(__file__).resolve().parents[3]
        for relative_path in (
            "src",
            "flext-core/src",
            "flext-cli/src",
            "flext-tests/src",
        ):
            monkeypatch.syspath_prepend(str(root / relative_path))
        importlib.invalidate_caches()
        for module_name in ("libs", "libs.versioning"):
            _ = sys.modules.pop(module_name, None)
        libs = importlib.import_module("libs")
        tm.that(libs.parse_semver("1.2.3"), eq=(1, 2, 3))
