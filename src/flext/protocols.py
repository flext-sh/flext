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
from flext_db_oracle import p
from flext_grpc import p as flext_grpc_p
from flext_infra import p as flext_infra_p
from flext_ldap import p as flext_ldap_p
from flext_meltano import p as flext_meltano_p
from flext_observability import p as flext_observability_p
from flext_oracle_oic import p as flext_oracle_oic_p
from flext_oracle_wms import p as flext_oracle_wms_p
from flext_plugin import p as flext_plugin_p
from flext_quality import p as flext_quality_p
from flext_tests import p as flext_tests_p


class FlextRootProtocols(
    flext_oracle_oic_p,
    flext_oracle_wms_p,
    flext_quality_p,
    flext_ldap_p,
    flext_infra_p,
    flext_meltano_p,
    flext_observability_p,
    flext_plugin_p,
    flext_tests_p,
    p,
    flext_grpc_p,
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
