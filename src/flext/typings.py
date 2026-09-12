"""Auto-generated facade to enforce MRO namespace contracts."""

from __future__ import annotations

from flext_core import m, t


class FlextRootTypes(t):
    """Flext types namespace."""

    class Root(t, m):
        """Root namespace for workspace-level types."""


t = FlextRootTypes

__all__: list[str] = ["FlextRootTypes", "t"]
