# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unified domain models facade for the FLEXT workspace.

Aggregates and exposes domain models, entity schemas, and value objects across
the member project hierarchy through a single canonical entry point ``m`` and
workspace namespace ``m.Root``. Preserves C3 MRO linearization order across
inherited subproject models.

See Also:
    - ADR-018: Generator Declarations.
    - ADR-027: Facade Single-Owner Law.
    - ADR-028: Facade Boundary Orchestrators Declarative Enforcement.
    - :mod:`flext.protocols`: Unified protocols facade.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext._models import FlextModelsRootBase, FlextModelsRootConfig
from flext_db_oracle import m
from flext_grpc import m as flext_grpc_m
from flext_infra import m as flext_infra_m
from flext_ldap import m as flext_ldap_m
from flext_meltano import m as flext_meltano_m
from flext_observability import m as flext_observability_m
from flext_oracle_oic import m as flext_oracle_oic_m
from flext_oracle_wms import m as flext_oracle_wms_m
from flext_plugin import m as flext_plugin_m
from flext_quality import m as flext_quality_m
from flext_tests import m as flext_tests_m


class FlextRootModels(
    flext_oracle_oic_m,
    flext_oracle_wms_m,
    flext_quality_m,
    flext_ldap_m,
    flext_infra_m,
    flext_meltano_m,
    flext_observability_m,
    flext_plugin_m,
    flext_tests_m,
    m,
    flext_grpc_m,
):
    """Unified root domain models facade.

    Provides access to domain entities, schemas, and payload types across all
    workspace packages. MRO is ordered by inheritance depth (deepest first)
    to guarantee deterministic C3 linearization across diamond dependencies.
    """

    class Root(FlextModelsRootBase, FlextModelsRootConfig):
        """Workspace-specific model classes accessed via ``m.Root.*``."""


m = FlextRootModels
"""Canonical models facade alias for the workspace."""

__all__: list[str] = ["FlextRootModels", "m"]
