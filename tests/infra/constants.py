"""FLEXT infra test helpers for constants."""

from __future__ import annotations

from typing import Final

from flext_tests import FlextTestsConstants


class TestsFlextRootConstants(FlextTestsConstants):
    class Workspace:
        """Workspace-level test constants."""

        class Tests:
            """Infrastructure test path constants."""

            MODULE_VERSIONING: Final[str] = "libs/versioning.py"


c = TestsFlextRootConstants

__all__: list[str] = ["TestsFlextRootConstants", "c"]
