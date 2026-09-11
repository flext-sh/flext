"""Release packaging contracts for the standalone workspace manager."""

from __future__ import annotations

import importlib.metadata
from collections.abc import Mapping
from importlib.resources import files
from pathlib import Path

from flext_core import t, u
from flext_tests import tm


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


class TestReleasePackaging:
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
        project = _section_of(loaded.unwrap(), "project")
        version = project["version"]
        if not isinstance(version, str):
            msg = "pyproject project.version must be a string"
            raise TypeError(msg)
        tm.that(importlib.metadata.version("flext"), eq=version)

    def test_root_distribution_is_bounded(self) -> None:
        """Release packaging excludes workspace-only repositories and state."""
        repository_root = Path(__file__).resolve().parents[2]
        loaded = u.config_load(repository_root / "pyproject.toml")
        tm.that(loaded.failure, eq=False)
        targets = _section_of(loaded.unwrap(), "tool", "hatch", "build", "targets")
        expected_sdist_includes = ["README.md", "pyproject.toml", "src/flext"]
        expected_wheel_packages = ["src/flext"]

        tm.that(_section_of(targets, "sdist")["only-include"], eq=expected_sdist_includes)
        tm.that(_section_of(targets, "wheel")["packages"], eq=expected_wheel_packages)
