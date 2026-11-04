# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export package for workspace root protocol declarations.

Defines PEP 562 lazy exports for structural subtyping protocols, value object
contracts, and configuration interfaces.

See Also:
    - ADR-018: Generator Declarations.
    - ADR-019: Service Contract Ports and Operations.
    - :mod:`flext.protocols`: Public protocols facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext._protocols.base import FlextRootProtocolsBase
    from flext._protocols.config import FlextRootProtocolsConfig
    from flext._protocols.generated_models_value import (
        FlextModelsRootProtocolsGeneratedValue,
    )


__all__: tuple[str, ...] = (
    "FlextModelsRootProtocolsGeneratedValue",
    "FlextRootProtocolsBase",
    "FlextRootProtocolsConfig",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextModelsRootProtocolsGeneratedValue": ".generated_models_value",
        "FlextRootProtocolsBase": ".base",
        "FlextRootProtocolsConfig": ".config",
    }),
    public_exports=__all__,
)
