from __future__ import annotations

from collections.abc import MutableSequence
from pathlib import Path
from types import ModuleType, SimpleNamespace

from flext_tests import FlextTestsTypes


class FlextWorkspaceTestTypes(FlextTestsTypes):
    class Workspace:
        """Workspace-level test type aliases."""

        class Tests:
            """Test infrastructure type definitions."""

            type Command = t.StrSequence
            type CommandBuffer = MutableSequence[Command]
            type LoadedModule = ModuleType
            type ProjectRef = SimpleNamespace
            type RepoCall = tuple[str, Path]


t = FlextWorkspaceTestTypes

__all__ = ["FlextWorkspaceTestTypes", "t"]
