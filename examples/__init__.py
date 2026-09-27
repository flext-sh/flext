# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext import c, m, p, settings, t, u

    from ._constants import FlextRootExamplesConstants
    from ._models import FlextRootExamplesModels, ValidationRules
    from .acl_validation import FlextRootAclValidator


__all__: tuple[str, ...] = (
    "FlextRootAclValidator",
    "FlextRootExamplesConstants",
    "FlextRootExamplesModels",
    "ValidationRules",
    "c",
    "m",
    "p",
    "settings",
    "t",
    "u",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._constants": ("FlextRootExamplesConstants",),
            "._models": ("FlextRootExamplesModels", "ValidationRules"),
            ".acl_validation": ("FlextRootAclValidator",),
            "flext": ("c", "m", "p", "settings", "t", "u"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
