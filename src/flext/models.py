# AUTO-GENERATED FILE — Regenerate with: make gen
"""Models facade for flext-workspace — m.Root project namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

import re
from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from flext._models import FlextModelsRootBase, FlextModelsRootConfig
from flext_db_oracle import FlextModelsDbOracle
from flext_grpc import FlextGrpcModels
from flext_infra import FlextInfraModels
from flext_ldap import FlextLdapModels
from flext_meltano import FlextMeltanoModels
from flext_observability import FlextObservabilityModels
from flext_oracle_oic import FlextModelsOracleOic
from flext_oracle_wms import FlextModelsOracleWms
from flext_plugin import FlextPluginModels
from flext_quality import FlextQualityModels
from flext_tests import FlextTestsModels


class FlextModelsRoot(
    FlextModelsOracleOic,
    FlextModelsOracleWms,
    FlextQualityModels,
    FlextLdapModels,
    FlextInfraModels,
    FlextMeltanoModels,
    FlextObservabilityModels,
    FlextPluginModels,
    FlextTestsModels,
    FlextModelsDbOracle,
    FlextGrpcModels,
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

__all__ = ("FlextModelsRoot", "m")
