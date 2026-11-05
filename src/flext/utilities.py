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

from flext_db_oracle import u
from flext_grpc import u as flext_grpc_u
from flext_infra import u as flext_infra_u
from flext_ldap import u as flext_ldap_u
from flext_meltano import u as flext_meltano_u
from flext_observability import u as flext_observability_u
from flext_oracle_oic import u as flext_oracle_oic_u
from flext_oracle_wms import u as flext_oracle_wms_u
from flext_plugin import u as flext_plugin_u
from flext_quality import u as flext_quality_u
from flext_tests import u as flext_tests_u


class FlextRootUtilities(
    flext_oracle_oic_u,
    flext_oracle_wms_u,
    flext_quality_u,
    flext_ldap_u,
    flext_infra_u,
    flext_meltano_u,
    flext_observability_u,
    flext_plugin_u,
    flext_tests_u,
    u,
    flext_grpc_u,
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
