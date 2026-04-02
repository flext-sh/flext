# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext import (
        constants,
        dev,
        docs,
        models,
        protocols,
        service,
        typings,
        utilities,
        workspace,
    )
    from flext.constants import FlextRootConstants, FlextRootConstants as c
    from flext.models import FlextRootModels, FlextRootModels as m
    from flext.protocols import FlextRootProtocols, FlextRootProtocols as p
    from flext.service import FlextRootServiceBase, s
    from flext.typings import FlexRootTypes, FlexRootTypes as t
    from flext.utilities import FlextRootUtilities, FlextRootUtilities as u
    from flext.workspace import main
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlexRootTypes": "flext.typings",
    "FlextRootConstants": "flext.constants",
    "FlextRootModels": "flext.models",
    "FlextRootProtocols": "flext.protocols",
    "FlextRootServiceBase": "flext.service",
    "FlextRootUtilities": "flext.utilities",
    "c": ("flext.constants", "FlextRootConstants"),
    "constants": "flext.constants",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "dev": "flext.dev",
    "docs": "flext.docs",
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext.models", "FlextRootModels"),
    "main": "flext.workspace",
    "models": "flext.models",
    "p": ("flext.protocols", "FlextRootProtocols"),
    "protocols": "flext.protocols",
    "r": ("flext_core.result", "FlextResult"),
    "s": "flext.service",
    "service": "flext.service",
    "t": ("flext.typings", "FlexRootTypes"),
    "typings": "flext.typings",
    "u": ("flext.utilities", "FlextRootUtilities"),
    "utilities": "flext.utilities",
    "workspace": "flext.workspace",
    "x": ("flext_core.mixins", "FlextMixins"),
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
