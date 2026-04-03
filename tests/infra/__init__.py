# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Infra package."""

from __future__ import annotations

import typing as _t

from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports
from flext_core.mixins import FlextMixins as x
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s
from tests.infra.constants import (
    FlextWorkspaceTestConstants,
    FlextWorkspaceTestConstants as c,
)
from tests.infra.models import (
    FlextWorkspaceTestModels,
    FlextWorkspaceTestModels as m,
)
from tests.infra.protocols import (
    FlextWorkspaceTestProtocols,
    FlextWorkspaceTestProtocols as p,
)
from tests.infra.typings import (
    FlextWorkspaceTestTypes,
    FlextWorkspaceTestTypes as t,
)
from tests.infra.utilities import (
    FlextWorkspaceTestUtilities,
    FlextWorkspaceTestUtilities as u,
)

if _t.TYPE_CHECKING:
    import tests.infra.constants as _tests_infra_constants

    constants = _tests_infra_constants
    import tests.infra.models as _tests_infra_models

    models = _tests_infra_models
    import tests.infra.protocols as _tests_infra_protocols

    protocols = _tests_infra_protocols
    import tests.infra.result as _tests_infra_result

    result = _tests_infra_result
    import tests.infra.typings as _tests_infra_typings

    typings = _tests_infra_typings
    import tests.infra.utilities as _tests_infra_utilities

    utilities = _tests_infra_utilities

    _ = (
        FlextWorkspaceTestConstants,
        FlextWorkspaceTestModels,
        FlextWorkspaceTestProtocols,
        FlextWorkspaceTestTypes,
        FlextWorkspaceTestUtilities,
        c,
        constants,
        d,
        e,
        h,
        m,
        models,
        p,
        protocols,
        r,
        result,
        s,
        t,
        typings,
        u,
        utilities,
        x,
    )
_LAZY_IMPORTS = {
    "FlextWorkspaceTestConstants": "tests.infra.constants",
    "FlextWorkspaceTestModels": "tests.infra.models",
    "FlextWorkspaceTestProtocols": "tests.infra.protocols",
    "FlextWorkspaceTestTypes": "tests.infra.typings",
    "FlextWorkspaceTestUtilities": "tests.infra.utilities",
    "c": ("tests.infra.constants", "FlextWorkspaceTestConstants"),
    "constants": "tests.infra.constants",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("tests.infra.models", "FlextWorkspaceTestModels"),
    "models": "tests.infra.models",
    "p": ("tests.infra.protocols", "FlextWorkspaceTestProtocols"),
    "protocols": "tests.infra.protocols",
    "r": ("flext_core.result", "FlextResult"),
    "result": "tests.infra.result",
    "s": ("flext_core.service", "FlextService"),
    "t": ("tests.infra.typings", "FlextWorkspaceTestTypes"),
    "typings": "tests.infra.typings",
    "u": ("tests.infra.utilities", "FlextWorkspaceTestUtilities"),
    "utilities": "tests.infra.utilities",
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "FlextWorkspaceTestConstants",
    "FlextWorkspaceTestModels",
    "FlextWorkspaceTestProtocols",
    "FlextWorkspaceTestTypes",
    "FlextWorkspaceTestUtilities",
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
