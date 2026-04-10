# AUTO-GENERATED FILE — Regenerate with: make gen
"""Infra package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.infra.constants as _tests_infra_constants
    import tests.infra.models as _tests_infra_models
    import tests.infra.protocols as _tests_infra_protocols
    import tests.infra.result as _tests_infra_result
    import tests.infra.typings as _tests_infra_typings
    import tests.infra.utilities as _tests_infra_utilities

    constants = _tests_infra_constants
    models = _tests_infra_models
    protocols = _tests_infra_protocols
    result = _tests_infra_result
    typings = _tests_infra_typings
    utilities = _tests_infra_utilities
    from tests.infra.constants import (
        TestsFlextInfraConstants,
        TestsFlextInfraConstants as c,
    )
    from tests.infra.models import TestsFlextTestModels, TestsFlextTestModels as m
    from tests.infra.protocols import (
        TestsFlextTestProtocols,
        TestsFlextTestProtocols as p,
    )
    from tests.infra.typings import TestsFlextTestTypes, TestsFlextTestTypes as t
    from tests.infra.utilities import (
        TestsFlextTestUtilities,
        TestsFlextTestUtilities as u,
    )

_LAZY_IMPORTS = {
    "TestsFlextInfraConstants": ("tests.infra.constants", "TestsFlextInfraConstants"),
    "TestsFlextTestModels": ("tests.infra.models", "TestsFlextTestModels"),
    "TestsFlextTestProtocols": ("tests.infra.protocols", "TestsFlextTestProtocols"),
    "TestsFlextTestTypes": ("tests.infra.typings", "TestsFlextTestTypes"),
    "TestsFlextTestUtilities": ("tests.infra.utilities", "TestsFlextTestUtilities"),
    "c": ("tests.infra.constants", "TestsFlextInfraConstants"),
    "constants": "tests.infra.constants",
    "m": ("tests.infra.models", "TestsFlextTestModels"),
    "models": "tests.infra.models",
    "p": ("tests.infra.protocols", "TestsFlextTestProtocols"),
    "protocols": "tests.infra.protocols",
    "result": "tests.infra.result",
    "t": ("tests.infra.typings", "TestsFlextTestTypes"),
    "typings": "tests.infra.typings",
    "u": ("tests.infra.utilities", "TestsFlextTestUtilities"),
    "utilities": "tests.infra.utilities",
}

__all__ = [
    "TestsFlextInfraConstants",
    "TestsFlextTestModels",
    "TestsFlextTestProtocols",
    "TestsFlextTestTypes",
    "TestsFlextTestUtilities",
    "c",
    "constants",
    "m",
    "models",
    "p",
    "protocols",
    "result",
    "t",
    "typings",
    "u",
    "utilities",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
