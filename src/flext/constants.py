"""Constants facade for flext-workspace — c.Root project namespace.

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
    FlextDbOracleConstants,
    FlextGrpcConstants,
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

__all__ = ("FlextRootConstants", "c")
