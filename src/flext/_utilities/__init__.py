# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export package for workspace root utility declarations.

Defines PEP 562 lazy exports for pure helper functions, conversion routines,
and configuration utility parsers.

See Also:
    - ADR-001: Railway-Oriented Programming.
    - ADR-027: Facade Single-Owner Law.
    - :mod:`flext.utilities`: Public utilities facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

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
