"""FLEXT infra test helpers for typings.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence
from pathlib import Path
from types import ModuleType, SimpleNamespace

from flext_infra import t
from flext_tests import FlextTestsTypes


class TestsFlextRootTypes(t):
    """Infrastructure test typings facade — extends flext_infra typings."""

    class _RootWorkspaceTypes:
        """Root workspace test-infrastructure type definitions."""

        type Command = t.StrSequence
        type CommandBuffer = MutableSequence[Command]
        type LoadedModule = ModuleType
        type ProjectRef = SimpleNamespace
        type RepoCall = tuple[str, Path]
        type RepoMetadata = tuple[str, str, str]  # owner, repo, branch

    class TestsFlextRoot(FlextTestsTypes.Tests, _RootWorkspaceTypes):
        """Test typings composing shared test + workspace type namespaces."""


__all__: list[str] = ["TestsFlextRootTypes"]
