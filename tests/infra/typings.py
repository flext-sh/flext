"""FLEXT infra test helpers for typings."""

from __future__ import annotations

from collections.abc import MutableSequence
from pathlib import Path
from types import ModuleType, SimpleNamespace

from flext_tests import t


class TestsFlextRootTypes(t):
    class Tests:
        """Test infrastructure type definitions."""

        type Command = t.StrSequence
        type CommandBuffer = MutableSequence[Command]
        type LoadedModule = ModuleType
        type ProjectRef = SimpleNamespace
        type RepoCall = tuple[str, Path]


__all__: list[str] = ["TestsFlextRootTypes"]
