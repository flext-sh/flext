# AUTO-GENERATED FILE — Regenerate with: make gen
"""Protocols facade for flext-workspace — p.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext._protocols import FlextRootProtocolsBase, FlextRootProtocolsConfig
from flext_db_oracle import p
from flext_grpc import p as flext_grpc_p
from flext_infra import p as flext_infra_p
from flext_ldap import p as flext_ldap_p
from flext_meltano import p as flext_meltano_p
from flext_observability import p as flext_observability_p
from flext_oracle_oic import p as flext_oracle_oic_p
from flext_oracle_wms import p as flext_oracle_wms_p
from flext_plugin import p as flext_plugin_p
from flext_quality import p as flext_quality_p
from flext_tests import p as flext_tests_p


class FlextRootProtocols(
    flext_oracle_oic_p,
    flext_oracle_wms_p,
    flext_quality_p,
    flext_ldap_p,
    flext_infra_p,
    flext_meltano_p,
    flext_observability_p,
    flext_plugin_p,
    flext_tests_p,
    p,
    flext_grpc_p,
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
__all__: list[str] = ["FlextRootProtocols", "p"]
