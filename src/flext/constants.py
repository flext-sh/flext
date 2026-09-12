"""Auto-generated facade to enforce MRO namespace contracts."""

from __future__ import annotations

from flext_core import c, t


class FlextRootConstants(c):
    """Flext constants namespace."""

    class Root(c, t):
        """Root namespace for workspace-level constants."""


c = FlextRootConstants

__all__: t.StrSequence = ("FlextRootConstants", "c")
