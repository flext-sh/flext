# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export package for workspace root configuration declarations.

Defines PEP 562 lazy exports for base configuration contracts and concrete
workspace settings schemas.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-018: Generator Declarations.
    - :mod:`flext.config`: Public configuration facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

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
