"""Release packaging contracts for the standalone workspace manager."""

from __future__ import annotations

import importlib.metadata
from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path

from flext_core import t, u
from flext_tests import tm


class TestsFlextRootReleasePackaging:
    @staticmethod
    def _section_of(payload: t.JsonMapping, *keys: str) -> t.JsonMapping:
        """Narrow a nested config section through runtime type checks."""
        node: t.JsonValue = dict(payload)
        for key in keys:
            if not isinstance(node, Mapping):
                msg = f"expected mapping at key {key!r}"
                raise TypeError(msg)
            node = node[key]
        if not isinstance(node, Mapping):
            msg = "expected final section to be a mapping"
            raise TypeError(msg)
        return node

    def test_cli_config_is_available_from_installed_package(self) -> None:
        """The CLI runtime owner must carry its declarative configuration."""
        config_file = files("flext_cli") / "config" / "cli.yaml"

        tm.that(config_file.is_file(), eq=True)

    def test_workspace_console_scripts_are_registered(self) -> None:
        """The published package must expose its complete entry-point contract."""
        entry_points = importlib.metadata.entry_points(group="console_scripts")
        names = {entry_point.name for entry_point in entry_points}

        for name in ("flext", "flext-dev", "flext-docs", "flext-workspace"):
            tm.that(name in names, eq=True)

    def test_installed_version_matches_version_owner(self) -> None:
        """Runtime metadata and the version SSOT must never diverge."""
        repository_root = Path(__file__).resolve().parents[2]
        loaded = u.config_load(repository_root / "pyproject.toml")
        tm.that(loaded.failure, eq=False)
        project = TestsFlextRootReleasePackaging._section_of(loaded.unwrap(), "project")
        version = project["version"]
        if not isinstance(version, str):
            msg = "pyproject project.version must be a string"
            raise TypeError(msg)
        tm.that(importlib.metadata.version("flext"), eq=version)
