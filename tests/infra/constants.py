"""FLEXT infra test helpers for constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from flext_infra import c


class TestsFlextRootConstants(c):
    """Infrastructure test constants facade — extends flext_infra constants."""

    class _WorkspaceConstants:
        """Workspace-level test constants."""

        MODULE_VERSIONING: Final[str] = "libs/versioning.py"

    class _RepoConstants:
        """Repository-level test constants."""

        DEFAULT_BRANCH: Final[str] = "main"

    class Tests(
        TestsFlextRootConstants._WorkspaceConstants,
        TestsFlextRootConstants._RepoConstants,
    ):
        """Test infrastructure constants."""


__all__: list[str] = ["TestsFlextRootConstants"]
