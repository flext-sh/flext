"""Utilities facade for flext-workspace — u.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext._utilities import FlextRootUtilitiesBase, FlextRootUtilitiesConfig
from flext_db_oracle import FlextDbOracleUtilities
from flext_grpc import FlextGrpcUtilities
from flext_infra import FlextInfraUtilities
from flext_ldap import FlextLdapUtilities
from flext_meltano import FlextMeltanoUtilities
from flext_observability import FlextObservabilityUtilities
from flext_oracle_oic import FlextOracleOicUtilities
from flext_oracle_wms import FlextOracleWmsUtilities
from flext_plugin import FlextPluginUtilities
from flext_quality import FlextQualityUtilities
from flext_tests import FlextTestsUtilities


class FlextRootUtilities(
    FlextOracleOicUtilities,
    FlextOracleWmsUtilities,
    FlextQualityUtilities,
    FlextLdapUtilities,
    FlextInfraUtilities,
    FlextMeltanoUtilities,
    FlextObservabilityUtilities,
    FlextPluginUtilities,
    FlextTestsUtilities,
    FlextDbOracleUtilities,
    FlextGrpcUtilities,
):
    """Workspace root utilities facade — access via u.Root.*.

    MRO ordered by inheritance depth (deepest first) to satisfy C3 linearization.
    FlextAuthUtilities is inherited via FlextOracleOicUtilities.
    FlextApiUtilities, FlextWebUtilities, FlextCliUtilities are inherited via
    the OracleOic/OracleWms/Quality paths.
    FlextLdifUtilities is inherited via FlextLdapUtilities.
    """

    class Root(FlextRootUtilitiesBase, FlextRootUtilitiesConfig):
        """Workspace root utilities MRO composition."""


u = FlextRootUtilities

__all__ = ("FlextRootUtilities", "u")
