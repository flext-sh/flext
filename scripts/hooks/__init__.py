# AUTO-GENERATED FILE — Regenerate with: make gen
"""Scripts.hooks package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext import c, m, p, t, u
__all__: tuple[str, ...] = ("c", "m", "p", "t", "u")

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({"flext": ("c", "m", "p", "t", "u")}),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
