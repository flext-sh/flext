# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unified utilities facade for the FLEXT workspace.

Aggregates and exposes pure helper functions, conversion routines, and railway
operations across the member project hierarchy through a single canonical entry
point ``u`` and workspace namespace ``u.Root``. Preserves C3 MRO linearization order
across inherited subproject utilities.

See Also:
    - ADR-001: Railway-Oriented Programming.
    - ADR-027: Facade Single-Owner Law.
    - ADR-028: Facade Boundary Orchestrators Declarative Enforcement.
    - :mod:`flext.constants`: Unified constants facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_db_oracle import FlextDbOracleUtilities
from flext_grpc import FlextGrpcUtilities
from flext_infra import FlextInfraUtilities
from flext_ldap import FlextLdapUtilities
from flext_meltano import FlextMeltanoUtilities
from flext_observability import FlextObservabilityUtilities
from flext_oracle_oic import FlextOracleOicUtilities
from flext_oracle_wms import FlextOracleWmsUtilities
from flext_plugin import FlextPluginUtilities
from flext_quality import FlextQualityUtilities
from flext_tests import FlextTestsUtilities


class FlextRootUtilities(
    FlextOracleOicUtilities,
    FlextOracleWmsUtilities,
    FlextQualityUtilities,
    FlextLdapUtilities,
    FlextInfraUtilities,
    FlextMeltanoUtilities,
    FlextObservabilityUtilities,
    FlextPluginUtilities,
    FlextTestsUtilities,
    FlextDbOracleUtilities,
    FlextGrpcUtilities,
):
    """Unified root utilities facade.

    Exposes shared algorithmic functions, railway result builders, and formatters
    across all workspace packages. MRO is ordered by inheritance depth (deepest first)
    to guarantee deterministic C3 linearization across diamond dependencies.
    """

    class Root:
        """Workspace-specific utility helpers accessed via ``u.Root.*``."""


u = FlextRootUtilities
"""Canonical utilities facade alias for the workspace."""

__all__: list[str] = ["FlextRootUtilities", "u"]
