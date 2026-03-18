from __future__ import annotations

from pathlib import Path
from types import ModuleType, SimpleNamespace

from flext_tests.typings import FlextTestsTypes


class FlextWorkspaceTestTypes(FlextTestsTypes):
    class Workspace:
        """Workspace-level test type aliases."""

        class Tests:
            """Test infrastructure type definitions."""

            type Command = list[str]
            type LoadedModule = ModuleType
            type ProjectRef = SimpleNamespace
            type RepoCall = tuple[str, Path]


t = FlextWorkspaceTestTypes

__all__ = ["FlextWorkspaceTestTypes", "t"]
