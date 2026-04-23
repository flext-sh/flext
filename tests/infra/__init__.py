# AUTO-GENERATED FILE — Regenerate with: make gen
"""Infra package."""

from __future__ import annotations

import typing as _t
from collections.abc import (
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

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
        TestsFlextRootConstants,
        TestsFlextRootConstants as c,
    )
    from tests.infra.models import TestsFlextRootModels, TestsFlextRootModels as m
    from tests.infra.protocols import (
        TestsFlextRootProtocols,
        TestsFlextRootProtocols as p,
    )
    from tests.infra.typings import TestsFlextRootTypes, TestsFlextRootTypes as t
    from tests.infra.utilities import (
        TestsFlextRootUtilities,
        TestsFlextRootUtilities as u,
    )

_LAZY_IMPORTS = {
    "TestsFlextRootConstants": ("tests.infra.constants", "TestsFlextRootConstants"),
    "TestsFlextRootModels": ("tests.infra.models", "TestsFlextRootModels"),
    "TestsFlextRootProtocols": ("tests.infra.protocols", "TestsFlextRootProtocols"),
    "TestsFlextRootTypes": ("tests.infra.typings", "TestsFlextRootTypes"),
    "TestsFlextRootUtilities": ("tests.infra.utilities", "TestsFlextRootUtilities"),
    "c": ("tests.infra.constants", "TestsFlextRootConstants"),
    "constants": "tests.infra.constants",
    "m": ("tests.infra.models", "TestsFlextRootModels"),
    "models": "tests.infra.models",
    "p": ("tests.infra.protocols", "TestsFlextRootProtocols"),
    "protocols": "tests.infra.protocols",
    "result": "tests.infra.result",
    "t": ("tests.infra.typings", "TestsFlextRootTypes"),
    "typings": "tests.infra.typings",
    "u": ("tests.infra.utilities", "TestsFlextRootUtilities"),
    "utilities": "tests.infra.utilities",
}

__all__: list[str] = [
    "TestsFlextRootConstants",
    "TestsFlextRootModels",
    "TestsFlextRootProtocols",
    "TestsFlextRootTypes",
    "TestsFlextRootUtilities",
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
