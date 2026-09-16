"""FLEXT infra test helpers for constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

<<<<<<< HEAD
from flext_core import c, t


class TestsFlextRootConstants(c):
    class TestsFlextRoot(c, t):
        """Root namespace for infra test constants."""

    class Workspace:
        """Workspace-level test constants."""
=======
from flext_infra import c


class _WorkspaceConstants:
    """Workspace-level test constants."""
>>>>>>> origin/0.12.0-dev

    MODULE_VERSIONING: Final[str] = "libs/versioning.py"


<<<<<<< HEAD
=======
class _RepoConstants:
    """Repository-level test constants."""

    DEFAULT_BRANCH: Final[str] = "main"


class TestsFlextRootConstants(c):
    """Infrastructure test constants facade — extends flext_infra constants."""

    class Tests(_WorkspaceConstants, _RepoConstants):
        """Test infrastructure constants."""


>>>>>>> origin/0.12.0-dev
__all__: list[str] = ["TestsFlextRootConstants"]
