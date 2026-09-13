"""FLEXT infra test helpers for typings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence
from pathlib import Path
from types import ModuleType, SimpleNamespace

from flext_tests import t


class _CommandTypes:
    """Command-related types."""

    type Command = t.StrSequence
    type CommandBuffer = MutableSequence[Command]


class _ModuleTypes:
    """Module-related types."""

    type LoadedModule = ModuleType
    type ProjectRef = SimpleNamespace


class _RepoTypes:
    """Repository-related types."""

    type RepoCall = tuple[str, Path]
    type RepoMetadata = tuple[str, str, str]  # owner, repo, branch


class TestsFlextRootTypes(t):
    """Infrastructure test typings facade — extends flext_tests typings."""

    class TestsFlextRoot(_CommandTypes, _ModuleTypes, _RepoTypes):
        """Test infrastructure type definitions."""


__all__: list[str] = ["TestsFlextRootTypes"]

