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
from flext_db_oracle import FlextDbOracleModels
from flext_grpc import FlextGrpcModels
from flext_infra import FlextInfraModels
from flext_ldap import FlextLdapModels
from flext_meltano import FlextMeltanoModels
from flext_observability import FlextObservabilityModels
from flext_oracle_oic import FlextOracleOicModels
from flext_oracle_wms import FlextOracleWmsModels
from flext_plugin import FlextPluginModels
from flext_quality import FlextQualityModels
from flext_tests import FlextTestsModels


class FlextRootModels(
    FlextOracleOicModels,
    FlextOracleWmsModels,
    FlextQualityModels,
    FlextLdapModels,
    FlextInfraModels,
    FlextMeltanoModels,
    FlextObservabilityModels,
    FlextPluginModels,
    FlextTestsModels,
    FlextDbOracleModels,
    FlextGrpcModels,
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
