"""FLEXT infra test helpers for constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import c

from typing import Final


class _WorkspaceConstants:
    """Workspace-level test constants."""

    MODULE_VERSIONING: Final[str] = "libs/versioning.py"


class _RepoConstants:
    """Repository-level test constants."""

    DEFAULT_BRANCH: Final[str] = "main"


class TestsFlextRootConstants(c):
    """Infrastructure test constants facade — extends flext_tests constants."""

    class TestsFlextRoot(_WorkspaceConstants, _RepoConstants):
        """Infrastructure test path constants."""


__all__: list[str] = ["TestsFlextRootConstants"]

