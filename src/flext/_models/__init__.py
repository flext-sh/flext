# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext._models.base import FlextRootModelsBase
    from flext._models.config import FlextRootModelsConfig


__all__: tuple[str, ...] = ("FlextRootModelsBase", "FlextRootModelsConfig")

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextRootModelsBase": ".base",
        "FlextRootModelsConfig": ".config",
    }),
    public_exports=__all__,
)
