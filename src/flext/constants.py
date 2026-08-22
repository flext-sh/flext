"""Auto-generated facade to enforce MRO namespace contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import c

if TYPE_CHECKING:
    from flext_core import t


class FlextRootConstants(c):
    """Flext constants namespace."""


c = FlextRootConstants

__all__: t.StrSequence = ("FlextRootConstants", "c")
