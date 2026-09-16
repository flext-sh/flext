"""FLEXT infra test helpers for typings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence
from pathlib import Path
from types import ModuleType, SimpleNamespace

<<<<<<< HEAD
from flext_core import m, t
from flext_tests import FlextTestsTypes


class TestsFlextRootTypes(t):
    class TestsFlextRoot(t, m):
        """Root namespace for infra test typings."""

    class Workspace:
        """Workspace-level test type aliases."""
=======
from flext_infra import t


class _CommandTypes:
    """Command-related types."""
>>>>>>> origin/0.12.0-dev

    type Command = t.StrSequence
    type CommandBuffer = MutableSequence[Command]


<<<<<<< HEAD
=======
class _ModuleTypes:
    """Module-related types."""

    type LoadedModule = ModuleType
    type ProjectRef = SimpleNamespace


class _RepoTypes:
    """Repository-related types."""

    type RepoCall = tuple[str, Path]
    type RepoMetadata = tuple[str, str, str]  # owner, repo, branch


class TestsFlextRootTypes(t):
    """Infrastructure test typings facade — extends flext_infra typings."""

    class Tests(_CommandTypes, _ModuleTypes, _RepoTypes):
        """Test infrastructure type definitions."""


>>>>>>> origin/0.12.0-dev
__all__: list[str] = ["TestsFlextRootTypes"]
