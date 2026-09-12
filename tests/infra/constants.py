"""FLEXT infra test helpers for constants."""

from __future__ import annotations

from typing import Final

from flext_core import c, t


class TestsFlextRootConstants(c):
    class TestsFlextRoot(c, t):
        """Root namespace for infra test constants."""

    class Workspace:
        """Workspace-level test constants."""

        class Tests:
            """Infrastructure test path constants."""

            MODULE_VERSIONING: Final[str] = "libs/versioning.py"


__all__: list[str] = ["TestsFlextRootConstants"]
