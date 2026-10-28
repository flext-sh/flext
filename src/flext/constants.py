# AUTO-GENERATED FILE — Regenerate with: make gen
"""Constants facade for flext-workspace — c.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext._constants import FlextRootConstantsBase, FlextRootConstantsConfig
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
    c,
    flext_grpc_c,
):
    """Workspace root constants facade — access via c.Root.*.

    MRO ordered by inheritance depth (deepest first) to satisfy C3 linearization.
    FlextAuthConstants is inherited via FlextOracleOicConstants.
    FlextApiConstants, FlextWebConstants, FlextCliConstants are inherited via
    the OracleOic/OracleWms/Quality paths.
    """

    class Root(FlextRootConstantsBase, FlextRootConstantsConfig):
        """Workspace root constants MRO composition."""


c = FlextRootConstants
__all__: list[str] = ["FlextRootConstants", "c"]
