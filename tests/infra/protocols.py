"""FLEXT infra test helpers for protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

<<<<<<< HEAD
from flext_core import c, p
=======
from flext_infra import p
>>>>>>> origin/0.12.0-dev

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from pathlib import Path
    from types import ModuleType


<<<<<<< HEAD
class TestsFlextRootProtocols(p):
    class TestsFlextRoot(p, c):
        """Root namespace for infra test protocols."""

    class Workspace:
        """Workspace-level test protocols."""
=======
class _ModuleProtocols:
    """Module resolution protocols."""
>>>>>>> origin/0.12.0-dev

    @runtime_checkable
    class SpecLoader(Protocol):
        """Protocol for module spec loaders."""

        def exec_module(self, module: ModuleType) -> None: ...

    @runtime_checkable
    class ModuleSpecProtocol(Protocol):
        """Protocol for module specifications."""

        name: str | None
        loader: _ModuleProtocols.SpecLoader | None

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


<<<<<<< HEAD
=======
class _RepoProtocols:
    """Repository metadata protocols."""

    @runtime_checkable
    class RepoProvider(Protocol):
        """Protocol for repository metadata providers."""

        def get_branch(self) -> str: ...
        def get_remote_url(self) -> str: ...


class TestsFlextRootProtocols(p):
    """Infrastructure test protocols facade — extends flext_infra protocols."""

    class Tests(_ModuleProtocols, _RepoProtocols):
        """Test infrastructure protocol definitions."""


>>>>>>> origin/0.12.0-dev
__all__: list[str] = ["TestsFlextRootProtocols"]
