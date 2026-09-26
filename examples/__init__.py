# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext import c, m, p, s, settings, t, u
    from flext_core import d, e, h, r, x

    from ._constants import FlextRootExamplesConstants
    from ._models import FlextRootExamplesModels, ValidationRules


__all__: tuple[str, ...] = (
    "FlextRootExamplesConstants",
    "FlextRootExamplesModels",
    "ValidationRules",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._constants": ("FlextRootExamplesConstants",),
            "._models": ("FlextRootExamplesModels", "ValidationRules"),
            "flext": ("c", "m", "p", "s", "settings", "t", "u"),
            "flext_core": ("d", "e", "h", "r", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
