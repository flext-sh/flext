"""Auto-generated facade to enforce MRO namespace contracts."""

from __future__ import annotations

from flext_core import c, p


class FlextRootProtocols(p):
    """Flext protocols namespace."""

    class Root(p, c):
        """Root namespace for workspace-level protocols."""


p = FlextRootProtocols

__all__: list[str] = ["FlextRootProtocols", "p"]
