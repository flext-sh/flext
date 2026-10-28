# AUTO-GENERATED FILE — Regenerate with: make gen
"""Typings facade for flext-workspace — t.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext._typings import FlextRootTypingsBase, FlextRootTypingsConfig
from flext_db_oracle import t
from flext_grpc import t as flext_grpc_t
from flext_infra import t as flext_infra_t
from flext_ldap import t as flext_ldap_t
from flext_meltano import t as flext_meltano_t
from flext_observability import t as flext_observability_t
from flext_oracle_oic import t as flext_oracle_oic_t
from flext_oracle_wms import t as flext_oracle_wms_t
from flext_plugin import t as flext_plugin_t
from flext_quality import t as flext_quality_t
from flext_tests import t as flext_tests_t


class FlextRootTypes(
    flext_oracle_oic_t,
    flext_oracle_wms_t,
    flext_quality_t,
    flext_ldap_t,
    flext_infra_t,
    flext_meltano_t,
    flext_observability_t,
    flext_plugin_t,
    flext_tests_t,
    t,
    flext_grpc_t,
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
__all__: list[str] = ["FlextRootTypes", "t"]
