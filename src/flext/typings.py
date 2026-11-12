# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unified typings facade for the FLEXT workspace.

Aggregates and exposes type aliases, typed mappings, and type-system markers
across the member project hierarchy through a single canonical entry point ``t``
and workspace namespace ``t.Root``. Preserves C3 MRO linearization order across
inherited subproject types.

See Also:
    - ADR-027: Facade Single-Owner Law.
    - ADR-028: Facade Boundary Orchestrators Declarative Enforcement.
    - :mod:`flext.protocols`: Unified protocols facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext._typings import FlextRootTypingsBase, FlextRootTypingsConfig
from flext_db_oracle import FlextDbOracleTypes
from flext_grpc import FlextGrpcTypes
from flext_infra import FlextInfraTypes
from flext_ldap import FlextLdapTypes
from flext_meltano import FlextMeltanoTypes
from flext_observability import FlextObservabilityTypes
from flext_oracle_oic import FlextOracleOicTypes
from flext_oracle_wms import FlextOracleWmsTypes
from flext_plugin import FlextPluginTypes
from flext_quality import FlextQualityTypes
from flext_tests import FlextTestsTypes


class FlextRootTypes(
    FlextOracleOicTypes,
    FlextOracleWmsTypes,
    FlextQualityTypes,
    FlextLdapTypes,
    FlextInfraTypes,
    FlextMeltanoTypes,
    FlextObservabilityTypes,
    FlextPluginTypes,
    FlextTestsTypes,
    FlextDbOracleTypes,
    FlextGrpcTypes,
):
    """Unified root typings facade.

    Exposes type aliases, union types, and type definitions across all workspace
    packages. MRO is ordered by inheritance depth (deepest first) to ensure
    deterministic C3 linearization across diamond dependencies.
    """

    class Root(FlextRootTypingsBase, FlextRootTypingsConfig):
        """Workspace-specific type aliases accessed via ``t.Root.*``."""


t = FlextRootTypes
"""Canonical typings facade alias for the workspace."""

__all__: list[str] = ["FlextRootTypes", "t"]
