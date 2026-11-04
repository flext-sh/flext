# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export package for workspace root constant declarations.

Defines PEP 562 lazy exports for base constant declarations and configuration
parameters across the workspace.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-018: Generator Declarations.
    - :mod:`flext.constants`: Public constants facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext._constants.base import FlextRootConstantsBase
    from flext._constants.config import FlextRootConstantsConfig


__all__: tuple[str, ...] = ("FlextRootConstantsBase", "FlextRootConstantsConfig")

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextRootConstantsBase": ".base",
        "FlextRootConstantsConfig": ".config",
    }),
    public_exports=__all__,
)
