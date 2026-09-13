"""FLEXT infra test helpers for constants."""

from __future__ import annotations

from typing import Final

from flext_tests import c


class TestsFlextRootConstants(c):
    class Tests:
        """Infrastructure test path constants."""

        class Workspace:
            """Workspace-level test constants."""

            MODULE_VERSIONING: Final[str] = "libs/versioning.py"


__all__: list[str] = ["TestsFlextRootConstants"]
