"""FLEXT infra test helpers for protocols."""

from __future__ import annotations

from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Protocol, runtime_checkable

from flext_tests import FlextTestsProtocols


class TestsFlextRootProtocols(FlextTestsProtocols):
    class Workspace:
        """Workspace-level test protocols."""

        class Tests:
            """Test infrastructure protocol definitions."""

            @runtime_checkable
            class SpecLoader(Protocol):
                """Protocol for module spec loaders."""

                def exec_module(self, module: ModuleType) -> None: ...

            @runtime_checkable
            class ModuleSpecProtocol(Protocol):
                """Protocol for module specifications."""

                name: str | None
                loader: TestsFlextRootProtocols.Workspace.Tests.SpecLoader | None

            @runtime_checkable
            class ModuleResolver(Protocol):
                """Protocol for module resolution callables."""

                def __call__(
                    self, module_name: str, relative_path: str, *, anchor_file: Path
                ) -> ModuleType: ...

            @runtime_checkable
            class ModuleSpecFactory(Protocol):
                """Protocol for module spec factory callables."""

                def __call__(self, name: str, location: Path) -> ModuleSpec | None: ...


p = TestsFlextRootProtocols

__all__: list[str] = ["TestsFlextRootProtocols", "p"]
