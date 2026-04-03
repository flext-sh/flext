# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Infra package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext import constants, models, protocols, result, typings, utilities
    from flext.constants import (
        FlextWorkspaceTestConstants,
        FlextWorkspaceTestConstants as c,
    )
    from flext.models import FlextWorkspaceTestModels, FlextWorkspaceTestModels as m
    from flext.protocols import (
        FlextWorkspaceTestProtocols,
        FlextWorkspaceTestProtocols as p,
    )
    from flext.result import r
    from flext.typings import FlextWorkspaceTestTypes, FlextWorkspaceTestTypes as t
    from flext.utilities import (
        FlextWorkspaceTestUtilities,
        FlextWorkspaceTestUtilities as u,
    )
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.service import FlextService as s

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextWorkspaceTestConstants": "flext.constants",
    "FlextWorkspaceTestModels": "flext.models",
    "FlextWorkspaceTestProtocols": "flext.protocols",
    "FlextWorkspaceTestTypes": "flext.typings",
    "FlextWorkspaceTestUtilities": "flext.utilities",
    "c": ("flext.constants", "FlextWorkspaceTestConstants"),
    "constants": "flext.constants",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext.models", "FlextWorkspaceTestModels"),
    "models": "flext.models",
    "p": ("flext.protocols", "FlextWorkspaceTestProtocols"),
    "protocols": "flext.protocols",
    "r": "flext.result",
    "result": "flext.result",
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext.typings", "FlextWorkspaceTestTypes"),
    "typings": "flext.typings",
    "u": ("flext.utilities", "FlextWorkspaceTestUtilities"),
    "utilities": "flext.utilities",
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
