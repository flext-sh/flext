# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unified constants facade for the FLEXT workspace.

Aggregates and exposes immutable constants across the member project hierarchy
through a single canonical entry point ``c`` and workspace namespace ``c.Root``.
Preserves C3 MRO linearization order across inherited subproject constants.

See Also:
    - ADR-005: Config, Settings, Constants, Templates, Schemas SSOT.
    - ADR-027: Facade Single-Owner Law.
    - ADR-028: Facade Boundary Orchestrators Declarative Enforcement.
    - :mod:`flext.models`: Unified domain models facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext._constants import FlextRootConstantsBase, FlextRootConstantsConfig
from flext_db_oracle import FlextDbOracleConstants
from flext_grpc import FlextGrpcConstants
from flext_infra import FlextInfraConstants
from flext_ldap import FlextLdapConstants
from flext_meltano import FlextMeltanoConstants
from flext_observability import FlextObservabilityConstants
from flext_oracle_oic import FlextOracleOicConstants
from flext_oracle_wms import FlextOracleWmsConstants
from flext_plugin import FlextPluginConstants
from flext_quality import FlextQualityConstants
from flext_tests import FlextTestsConstants


class FlextRootConstants(
    FlextOracleOicConstants,
    FlextOracleWmsConstants,
    FlextQualityConstants,
    FlextLdapConstants,
    FlextInfraConstants,
    FlextMeltanoConstants,
    FlextObservabilityConstants,
    FlextPluginConstants,
    FlextTestsConstants,
    FlextGrpcConstants,
    FlextDbOracleConstants,
):
    """Unified root constants facade.

    Exposes constant values across all workspace packages via class attributes
    and provides workspace-specific constants under the ``Root`` namespace.
    MRO is ordered by inheritance depth (deepest first) to ensure deterministic
    C3 linearization across multi-project diamond dependencies.
    """

    class Root(FlextRootConstantsBase, FlextRootConstantsConfig):
        """Workspace-specific constants namespace accessed via ``c.Root.*``."""


c = FlextRootConstants
"""Canonical constants facade alias for the workspace."""

__all__: list[str] = ["FlextRootConstants", "c"]
