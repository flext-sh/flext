# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext import c, config, m, p, settings, t, u

    from examples._constants import FlextRootExamplesConstants


__all__: tuple[str, ...] = (
    "FlextRootExamplesConstants",
    "c",
    "config",
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
            "flext": ("c", "config", "m", "p", "settings", "t", "u"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
