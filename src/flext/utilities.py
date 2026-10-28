# AUTO-GENERATED FILE — Regenerate with: make gen
"""Utilities facade for flext-workspace — u.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext._utilities import FlextRootUtilitiesBase, FlextRootUtilitiesConfig
from flext_db_oracle import u
from flext_grpc import u as flext_grpc_u
from flext_infra import u as flext_infra_u
from flext_ldap import u as flext_ldap_u
from flext_meltano import u as flext_meltano_u
from flext_observability import u as flext_observability_u
from flext_oracle_oic import u as flext_oracle_oic_u
from flext_oracle_wms import u as flext_oracle_wms_u
from flext_plugin import u as flext_plugin_u
from flext_quality import u as flext_quality_u
from flext_tests import u as flext_tests_u


class FlextRootUtilities(
    flext_oracle_oic_u,
    flext_oracle_wms_u,
    flext_quality_u,
    flext_ldap_u,
    flext_infra_u,
    flext_meltano_u,
    flext_observability_u,
    flext_plugin_u,
    flext_tests_u,
    u,
    flext_grpc_u,
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
__all__: list[str] = ["FlextRootUtilities", "u"]
