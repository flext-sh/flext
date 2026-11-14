"""Configuration management protocols for the FLEXT workspace root.

Specifies structural interfaces and contracts required for configuration providers,
settings injectors, and dynamic environment resolvers.

See Also:
    - ADR-016: Settings & Config Singleton Contract.
    - ADR-019: Service Contract Ports and Operations.
    - :class:`flext._protocols.base.FlextRootProtocolsBase`: Foundational protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext import t
from flext_oracle_oic import FlextOracleOicProtocols


class FlextRootProtocolsConfig:
    """Structural protocol for configuration providers and resolvers.

    Defines expected attributes and methods for configuration consumers to interact
    with settings without coupling to concrete configuration classes.
    """

    @runtime_checkable
    class PipelinePayload(FlextOracleOicProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        values: t.MutableJsonMapping

    @runtime_checkable
    class PipelineStageData(FlextOracleOicProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def data(self) -> FlextRootProtocolsConfig.PipelinePayload:
            """Payload produced by the preceding pipeline stage."""
            ...


__all__ = ("FlextRootProtocolsConfig",)
