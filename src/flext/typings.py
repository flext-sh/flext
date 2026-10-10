"""Typings facade for flext-workspace — t.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext._typings import FlextRootTypingsBase, FlextRootTypingsConfig
from flext_db_oracle import FlextDbOracleTypes
from flext_grpc import FlextGrpcTypes
from flext_infra import FlextInfraTypes
from flext_ldap import FlextLdapTypes
from flext_meltano import FlextMeltanoTypes
from flext_observability import FlextObservabilityTypes
from flext_oracle_oic import FlextOracleOicTypes
from flext_oracle_wms import FlextOracleWmsTypes
from flext_plugin import FlextPluginTypes
from flext_quality import FlextQualityTypes
from flext_tests import FlextTestsTypes


class FlextRootTypes(
    FlextOracleOicTypes,
    FlextOracleWmsTypes,
    FlextQualityTypes,
    FlextLdapTypes,
    FlextInfraTypes,
    FlextMeltanoTypes,
    FlextObservabilityTypes,
    FlextPluginTypes,
    FlextTestsTypes,
    FlextDbOracleTypes,
    FlextGrpcTypes,
):
    """Workspace root typings facade — access via t.Root.*.

    MRO ordered by inheritance depth (deepest first) to satisfy C3 linearization.
    FlextAuthTypes is inherited via FlextOracleOicTypes.
    FlextApiTypes, FlextWebTypes, FlextCliTypes are inherited via
    the OracleOic/OracleWms/Quality paths.
    FlextLdifTypes is inherited via FlextLdapTypes.
    """

    class Root(FlextRootTypingsBase, FlextRootTypingsConfig):
        """Workspace root typings MRO composition."""


t = FlextRootTypes

__all__ = ("FlextRootTypes", "t")
