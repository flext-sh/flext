from __future__ import annotations

from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Protocol, runtime_checkable

from flext_tests.protocols import FlextTestsProtocols


class FlextWorkspaceTestProtocols(FlextTestsProtocols):
    class Workspace:
        class Tests:
            @runtime_checkable
            class SpecLoader(Protocol):
                def exec_module(self, module: ModuleType) -> None: ...

            @runtime_checkable
            class ModuleSpecProtocol(Protocol):
                name: str | None
                loader: object | None

            @runtime_checkable
            class ModuleResolver(Protocol):
                def __call__(
                    self,
                    module_name: str,
                    relative_path: str,
                    *,
                    anchor_file: Path,
                ) -> ModuleType: ...

            @runtime_checkable
            class ModuleSpecFactory(Protocol):
                def __call__(self, name: str, location: Path) -> ModuleSpec | None: ...


p = FlextWorkspaceTestProtocols

__all__ = ["FlextWorkspaceTestProtocols", "p"]
