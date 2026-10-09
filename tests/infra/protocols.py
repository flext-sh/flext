"""FLEXT infra test helpers for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext import p
from flext_tests import FlextTestsProtocols

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from pathlib import Path
    from types import ModuleType


class TestsFlextRootProtocols(p):
    """Infrastructure test protocols facade — extends flext_infra protocols."""

    class Tests(FlextTestsProtocols.Tests):
        """Test protocols composing shared test + workspace protocol namespaces."""

        @runtime_checkable
        class SpecLoader(Protocol):
            """Protocol for module spec loaders."""

            def exec_module(self, module: ModuleType) -> None:
                """Execute the loaded module in its namespace."""

        @runtime_checkable
        class ModuleSpecProtocol(Protocol):
            """Protocol for module specifications."""

            name: str | None
            loader: TestsFlextRootProtocols.Tests.SpecLoader | None

        @runtime_checkable
        class ModuleResolver(Protocol):
            """Protocol for module resolution callables."""

            def __call__(
                self,
                module_name: str,
                relative_path: str,
                *,
                anchor_file: Path,
            ) -> ModuleType:
                """Resolve one module name from its relative path."""
                ...

        @runtime_checkable
        class ModuleSpecFactory(Protocol):
            """Protocol for module spec factory callables."""

            def __call__(self, name: str, location: Path) -> ModuleSpec | None:
                """Build one module spec from a name and file location."""

        @runtime_checkable
        class RepoProvider(Protocol):
            """Protocol for repository metadata providers."""

            def get_branch(self) -> str:
                """Return the repository active branch name."""
                ...

            def get_remote_url(self) -> str:
                """Return the repository remote URL."""
                ...


__all__: list[str] = ["TestsFlextRootProtocols"]
