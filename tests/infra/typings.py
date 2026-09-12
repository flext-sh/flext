"""FLEXT infra test helpers for typings."""

from __future__ import annotations

from collections.abc import MutableSequence
from pathlib import Path
from types import ModuleType, SimpleNamespace

from flext_core import m, t
from flext_tests import FlextTestsTypes


class TestsFlextRootTypes(t):
    class TestsFlextRoot(t, m):
        """Root namespace for infra test typings."""

    class Workspace:
        """Workspace-level test type aliases."""

        class Tests:
            """Test infrastructure type definitions."""

            type Command = FlextTestsTypes.StrSequence
            type CommandBuffer = MutableSequence[Command]
            type LoadedModule = ModuleType
            type ProjectRef = SimpleNamespace
            type RepoCall = tuple[str, Path]


__all__: list[str] = ["TestsFlextRootTypes"]
