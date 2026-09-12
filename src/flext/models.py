"""Auto-generated facade to enforce MRO namespace contracts."""

from __future__ import annotations

from flext_core import m, t


class FlextRootModels(m):
    """Flext models namespace."""

    class Root(m, t):
        """Root namespace for workspace-level models."""


m = FlextRootModels

__all__: list[str] = ["FlextRootModels", "m"]
