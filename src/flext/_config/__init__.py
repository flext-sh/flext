# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext. Config package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext._config.base import FlextRootConfigBase
    from flext._config.config import FlextRootConfigConfig


__all__: tuple[str, ...] = ("FlextRootConfigBase", "FlextRootConfigConfig")

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextRootConfigBase": ".base",
        "FlextRootConfigConfig": ".config",
    }),
    public_exports=__all__,
)
