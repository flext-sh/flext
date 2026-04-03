# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Infra package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core._constants.mixins import FlextConstantsMixins as x
    from flext_core._models.decorators import FlextModelsDecorators as d
    from flext_core._models.service import FlextModelsService as s
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from tests.infra import constants, models, protocols, result, typings, utilities
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
    from tests.infra.result import r
    from tests.infra.typings import (
        FlextWorkspaceTestTypes,
        FlextWorkspaceTestTypes as t,
    )
    from tests.infra.utilities import (
        FlextWorkspaceTestUtilities,
        FlextWorkspaceTestUtilities as u,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextWorkspaceTestConstants": "tests.infra.constants",
    "FlextWorkspaceTestModels": "tests.infra.models",
    "FlextWorkspaceTestProtocols": "tests.infra.protocols",
    "FlextWorkspaceTestTypes": "tests.infra.typings",
    "FlextWorkspaceTestUtilities": "tests.infra.utilities",
    "c": ("tests.infra.constants", "FlextWorkspaceTestConstants"),
    "constants": "tests.infra.constants",
    "d": ("flext_core._models.decorators", "FlextModelsDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("tests.infra.models", "FlextWorkspaceTestModels"),
    "models": "tests.infra.models",
    "p": ("tests.infra.protocols", "FlextWorkspaceTestProtocols"),
    "protocols": "tests.infra.protocols",
    "r": "tests.infra.result",
    "result": "tests.infra.result",
    "s": ("flext_core._models.service", "FlextModelsService"),
    "t": ("tests.infra.typings", "FlextWorkspaceTestTypes"),
    "typings": "tests.infra.typings",
    "u": ("tests.infra.utilities", "FlextWorkspaceTestUtilities"),
    "utilities": "tests.infra.utilities",
    "x": ("flext_core._constants.mixins", "FlextConstantsMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
