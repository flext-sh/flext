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
from flext_db_oracle import t
from flext_grpc import t as flext_grpc_t
from flext_infra import t as flext_infra_t
from flext_ldap import t as flext_ldap_t
from flext_meltano import t as flext_meltano_t
from flext_observability import t as flext_observability_t
from flext_oracle_oic import t as flext_oracle_oic_t
from flext_oracle_wms import t as flext_oracle_wms_t
from flext_plugin import t as flext_plugin_t
from flext_quality import t as flext_quality_t
from flext_tests import t as flext_tests_t


class FlextRootTypes(
    flext_oracle_oic_t,
    flext_oracle_wms_t,
    flext_quality_t,
    flext_ldap_t,
    flext_infra_t,
    flext_meltano_t,
    flext_observability_t,
    flext_plugin_t,
    flext_tests_t,
    t,
    flext_grpc_t,
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
