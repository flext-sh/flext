# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext. Utilities package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext._utilities.base import FlextRootUtilitiesBase
    from flext._utilities.config import FlextRootUtilitiesConfig


__all__: tuple[str, ...] = ("FlextRootUtilitiesBase", "FlextRootUtilitiesConfig")

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextRootUtilitiesBase": ".base",
        "FlextRootUtilitiesConfig": ".config",
    }),
    public_exports=__all__,
)
