# AUTO-GENERATED FILE — Regenerate with: make gen
"""Models facade for flext-workspace — m.Root project namespace.

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


class FlextModelsRoot(
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
    """Workspace root models facade — access via m.Root.*.

    MRO ordered by inheritance depth (deepest first) to satisfy C3 linearization.
    FlextAuthModels is inherited via FlextModelsOracleOic.
    FlextApiModels, FlextWebModels, FlextCliModels are inherited via
    the OracleOic/OracleWms/Quality paths.
    FlextLdifModels is inherited via FlextLdapModels.
    """

    class Root(FlextModelsRootBase, FlextModelsRootConfig):
        """Workspace root models MRO composition."""


m = FlextModelsRoot
__all__: list[str] = ["FlextModelsRoot", "m"]
