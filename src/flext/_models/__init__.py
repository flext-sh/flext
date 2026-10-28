# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext._models.base import FlextModelsRootBase
    from flext._models.config import FlextModelsRootConfig


__all__: tuple[str, ...] = ("FlextModelsRootBase", "FlextModelsRootConfig")

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextModelsRootBase": ".base",
        "FlextModelsRootConfig": ".config",
    }),
    public_exports=__all__,
)
