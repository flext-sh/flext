# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unified protocols facade for the FLEXT workspace.

Aggregates and exposes structural typing protocols and interface contracts across
the member project hierarchy through a single canonical entry point ``p`` and
workspace namespace ``p.Root``. Preserves C3 MRO linearization order across
inherited subproject protocols.

See Also:
    - ADR-018: Generator Declarations.
    - ADR-019: Service Contract Ports and Operations.
    - ADR-027: Facade Single-Owner Law.
    - :mod:`flext.typings`: Unified typings facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext._protocols import (
    FlextModelsRootProtocolsGeneratedValue,
    FlextRootProtocolsBase,
    FlextRootProtocolsConfig,
)
from flext_db_oracle import FlextDbOracleProtocols
from flext_grpc import FlextGrpcProtocols
from flext_infra import FlextInfraProtocols
from flext_ldap import FlextLdapProtocols
from flext_meltano import FlextMeltanoProtocols
from flext_observability import FlextObservabilityProtocols
from flext_oracle_oic import FlextOracleOicProtocols
from flext_oracle_wms import FlextOracleWmsProtocols
from flext_plugin import FlextPluginProtocols
from flext_quality import FlextQualityProtocols
from flext_tests import FlextTestsProtocols


class FlextRootProtocols(
    FlextOracleOicProtocols,
    FlextOracleWmsProtocols,
    FlextQualityProtocols,
    FlextLdapProtocols,
    FlextInfraProtocols,
    FlextMeltanoProtocols,
    FlextObservabilityProtocols,
    FlextPluginProtocols,
    FlextTestsProtocols,
    FlextDbOracleProtocols,
    FlextGrpcProtocols,
):
    """Unified root protocols facade.

    Exposes structural interface contracts across all workspace packages and
    provides root workspace protocol specifications under the ``Root`` namespace.
    MRO is ordered by inheritance depth (deepest first) to ensure deterministic
    C3 linearization across multi-project dependencies.
    """

    class Root(
        FlextRootProtocolsBase,
        FlextRootProtocolsConfig,
        FlextModelsRootProtocolsGeneratedValue,
    ):
        """Workspace-specific protocol contracts accessed via ``p.Root.*``."""


p = FlextRootProtocols
"""Canonical protocols facade alias for the workspace."""

__all__: list[str] = ["FlextRootProtocols", "p"]
