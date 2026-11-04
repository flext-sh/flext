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

from flext._constants.base import FlextRootConstantsBase
from flext._constants.config import FlextRootConstantsConfig
from flext_db_oracle import c
from flext_grpc import c as flext_grpc_c
from flext_infra import c as flext_infra_c
from flext_ldap import c as flext_ldap_c
from flext_meltano import c as flext_meltano_c
from flext_observability import c as flext_observability_c
from flext_oracle_oic import c as flext_oracle_oic_c
from flext_oracle_wms import c as flext_oracle_wms_c
from flext_plugin import c as flext_plugin_c
from flext_quality import c as flext_quality_c
from flext_tests import c as flext_tests_c


class FlextRootConstants(
    flext_oracle_oic_c,
    flext_oracle_wms_c,
    flext_quality_c,
    flext_ldap_c,
    flext_infra_c,
    flext_meltano_c,
    flext_observability_c,
    flext_plugin_c,
    flext_tests_c,
    flext_grpc_c,
    c,
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
