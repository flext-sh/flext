"""Models facade for flext-workspace — m.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext._models import FlextRootModelsBase, FlextRootModelsConfig
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
    """Workspace root models facade — access via m.Root.*.

    MRO ordered by inheritance depth (deepest first) to satisfy C3 linearization.
    FlextAuthModels is inherited via FlextOracleOicModels.
    FlextApiModels, FlextWebModels, FlextCliModels are inherited via
    the OracleOic/OracleWms/Quality paths.
    FlextLdifModels is inherited via FlextLdapModels.
    """

    class Root(FlextRootModelsBase, FlextRootModelsConfig):
        """Workspace root models MRO composition."""


m = FlextRootModels

__all__ = ("FlextRootModels", "m")
