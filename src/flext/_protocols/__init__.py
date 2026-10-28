# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext. Protocols package.

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
        FlextRootProtocolsGeneratedModelsValue,
    )


__all__: tuple[str, ...] = (
    "FlextRootProtocolsBase",
    "FlextRootProtocolsConfig",
    "FlextRootProtocolsGeneratedModelsValue",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextRootProtocolsBase": ".base",
        "FlextRootProtocolsConfig": ".config",
        "FlextRootProtocolsGeneratedModelsValue": ".generated_models_value",
    }),
    public_exports=__all__,
)
