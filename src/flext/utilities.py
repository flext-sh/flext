"""Auto-generated facade to enforce MRO namespace contracts."""

from __future__ import annotations

from flext_core import t, u


class FlextRootUtilities(u):
    """Flext utilities namespace."""

    class Root(u, t):
        """Root namespace for workspace-level utilities."""


u = FlextRootUtilities

__all__: list[str] = ["FlextRootUtilities", "u"]
