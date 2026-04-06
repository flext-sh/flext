# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Infra package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.infra.constants as _tests_infra_constants

    constants = _tests_infra_constants
    import tests.infra.models as _tests_infra_models
    from tests.infra.constants import (
        TestsFlextInfraConstants,
        TestsFlextInfraConstants as c,
    )

    models = _tests_infra_models
    import tests.infra.protocols as _tests_infra_protocols
    from tests.infra.models import TestsFlextTestModels, TestsFlextTestModels as m

    protocols = _tests_infra_protocols
    import tests.infra.result as _tests_infra_result
    from tests.infra.protocols import (
        TestsFlextTestProtocols,
        TestsFlextTestProtocols as p,
    )

    result = _tests_infra_result
    import tests.infra.typings as _tests_infra_typings

    typings = _tests_infra_typings
    import tests.infra.utilities as _tests_infra_utilities
    from tests.infra.typings import TestsFlextTestTypes, TestsFlextTestTypes as t

    utilities = _tests_infra_utilities
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
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
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("tests.infra.models", "TestsFlextTestModels"),
    "models": "tests.infra.models",
    "p": ("tests.infra.protocols", "TestsFlextTestProtocols"),
    "protocols": "tests.infra.protocols",
    "r": ("flext_core.result", "FlextResult"),
    "result": "tests.infra.result",
    "s": ("flext_core.service", "FlextService"),
    "t": ("tests.infra.typings", "TestsFlextTestTypes"),
    "typings": "tests.infra.typings",
    "u": ("tests.infra.utilities", "TestsFlextTestUtilities"),
    "utilities": "tests.infra.utilities",
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "TestsFlextInfraConstants",
    "TestsFlextTestModels",
    "TestsFlextTestProtocols",
    "TestsFlextTestTypes",
    "TestsFlextTestUtilities",
    "c",
    "constants",
    "d",
    "e",
    "h",
    "m",
    "models",
    "p",
    "protocols",
    "r",
    "result",
    "s",
    "t",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
