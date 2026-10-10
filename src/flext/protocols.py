"""Protocols facade for flext-workspace — p.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext._protocols import FlextRootProtocolsBase, FlextRootProtocolsConfig
from flext_db_oracle import FlextDbOracleProtocols
from flext_grpc import FlextGrpcProtocols
from flext_infra import FlextInfraProtocols
from flext_ldap import FlextLdapProtocols
from flext_meltano import FlextMeltanoProtocols
from flext_observability import FlextObservabilityProtocols
from flext_oracle_oic import FlextOracleOicProtocols
from flext_oracle_wms import FlextOracleWmsProtocols
from flext_plugin import FlextPluginProtocols
from flext_quality import FlextQualityProtocols
from flext_tests import FlextTestsProtocols


class FlextRootProtocols(
    FlextOracleOicProtocols,
    FlextOracleWmsProtocols,
    FlextQualityProtocols,
    FlextLdapProtocols,
    FlextInfraProtocols,
    FlextMeltanoProtocols,
    FlextObservabilityProtocols,
    FlextPluginProtocols,
    FlextTestsProtocols,
    FlextDbOracleProtocols,
    FlextGrpcProtocols,
):
    """Workspace root protocols facade — access via p.Root.*.

    MRO ordered by inheritance depth (deepest first) to satisfy C3 linearization.
    FlextAuthProtocols is inherited via FlextOracleOicProtocols.
    FlextApiProtocols, FlextWebProtocols, FlextCliProtocols are inherited via
    the OracleOic/OracleWms/Quality paths.
    FlextLdifProtocols is inherited via FlextLdapProtocols.
    """

    class Root(FlextRootProtocolsBase, FlextRootProtocolsConfig):
        """Workspace root protocols MRO composition."""


p = FlextRootProtocols

__all__ = ("FlextRootProtocols", "p")
