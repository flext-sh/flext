"""FLEXT infra test helpers for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import p

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from pathlib import Path
    from types import ModuleType


class TestsFlextRootProtocols(p):
    """Infrastructure test protocols facade — extends flext_tests protocols."""

    class TestsFlextRoot:
        """Test infrastructure protocol definitions."""

        @runtime_checkable
        class SpecLoader(Protocol):
            """Protocol for module spec loaders."""

            def exec_module(self, module: ModuleType) -> None: ...

        @runtime_checkable
        class ModuleSpecProtocol(Protocol):
            """Protocol for module specifications."""

            name: str | None
            loader: TestsFlextRootProtocols.TestsFlextRoot.SpecLoader | None

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


__all__: list[str] = ["TestsFlextRootProtocols"]

