# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext package."""

from __future__ import annotations

import typing as _t

from flext.constants import FlextRootConstants, FlextRootConstants as c
from flext.models import FlextRootModels, FlextRootModels as m
from flext.protocols import FlextRootProtocols, FlextRootProtocols as p
from flext.service import FlextRootServiceBase
from flext.typings import FlexRootTypes, FlexRootTypes as t
from flext.utilities import FlextRootUtilities, FlextRootUtilities as u
from flext.workspace import main
from flext_core.decorators import FlextDecorators as d
from flext_core.exceptions import FlextExceptions as e
from flext_core.handlers import FlextHandlers as h
from flext_core.lazy import install_lazy_exports
from flext_core.mixins import FlextMixins as x
from flext_core.result import FlextResult as r
from flext_core.service import FlextService as s

if _t.TYPE_CHECKING:
    import flext.constants as _flext_constants

    constants = _flext_constants
    import flext.dev as _flext_dev

    dev = _flext_dev
    import flext.docs as _flext_docs

    docs = _flext_docs
    import flext.models as _flext_models

    models = _flext_models
    import flext.protocols as _flext_protocols

    protocols = _flext_protocols
    import flext.service as _flext_service

    service = _flext_service
    import flext.typings as _flext_typings

    typings = _flext_typings
    import flext.utilities as _flext_utilities

    utilities = _flext_utilities
    import flext.workspace as _flext_workspace

    workspace = _flext_workspace

    _ = (
        FlexRootTypes,
        FlextRootConstants,
        FlextRootModels,
        FlextRootProtocols,
        FlextRootServiceBase,
        FlextRootUtilities,
        c,
        constants,
        d,
        dev,
        docs,
        e,
        h,
        m,
        main,
        models,
        p,
        protocols,
        r,
        s,
        service,
        t,
        typings,
        u,
        utilities,
        workspace,
        x,
    )
_LAZY_IMPORTS = {
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
    "s": ("flext_core.service", "FlextService"),
    "service": "flext.service",
    "t": ("flext.typings", "FlexRootTypes"),
    "typings": "flext.typings",
    "u": ("flext.utilities", "FlextRootUtilities"),
    "utilities": "flext.utilities",
    "workspace": "flext.workspace",
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "FlexRootTypes",
    "FlextRootConstants",
    "FlextRootModels",
    "FlextRootProtocols",
    "FlextRootServiceBase",
    "FlextRootUtilities",
    "c",
    "constants",
    "d",
    "dev",
    "docs",
    "e",
    "h",
    "m",
    "main",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "service",
    "t",
    "typings",
    "u",
    "utilities",
    "workspace",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
