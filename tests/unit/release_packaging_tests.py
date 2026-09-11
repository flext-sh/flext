"""Release packaging contracts for the standalone workspace manager."""

from __future__ import annotations

import importlib.metadata
import tomllib
from importlib.resources import files
from pathlib import Path

from flext_tests import tm


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
        payload = tomllib.loads(
            (repository_root / "pyproject.toml").read_text(encoding="utf-8")
        )

        tm.that(importlib.metadata.version("flext"), eq=payload["project"]["version"])

    def test_root_distribution_is_bounded(self) -> None:
        """Release packaging excludes workspace-only repositories and state."""
        repository_root = Path(__file__).resolve().parents[2]
        payload = tomllib.loads(
            (repository_root / "pyproject.toml").read_text(encoding="utf-8")
        )
        targets = payload["tool"]["hatch"]["build"]["targets"]
        expected_sdist_includes = ["README.md", "pyproject.toml", "src/flext"]
        expected_wheel_packages = ["src/flext"]

        tm.that(targets["sdist"]["only-include"], eq=expected_sdist_includes)
        tm.that(targets["wheel"]["packages"], eq=expected_wheel_packages)
