# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext._protocols.base import FlextRootProtocolsBase
    from flext._protocols.config import FlextRootProtocolsConfig


__all__: tuple[str, ...] = ("FlextRootProtocolsBase", "FlextRootProtocolsConfig")

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("FlextRootProtocolsBase",),
            ".config": ("FlextRootProtocolsConfig",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
