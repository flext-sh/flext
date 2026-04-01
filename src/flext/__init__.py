# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes, d, e, h, r, x

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

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlexRootTypes": "flext.typings",
    "FlextRootConstants": "flext.constants",
    "FlextRootModels": "flext.models",
    "FlextRootProtocols": "flext.protocols",
    "FlextRootServiceBase": "flext.service",
    "FlextRootUtilities": "flext.utilities",
    "c": ("flext.constants", "FlextRootConstants"),
    "constants": "flext.constants",
    "d": "flext_core",
    "dev": "flext.dev",
    "docs": "flext.docs",
    "e": "flext_core",
    "h": "flext_core",
    "m": ("flext.models", "FlextRootModels"),
    "main": "flext.workspace",
    "models": "flext.models",
    "p": ("flext.protocols", "FlextRootProtocols"),
    "protocols": "flext.protocols",
    "r": "flext_core",
    "s": "flext.service",
    "service": "flext.service",
    "t": ("flext.typings", "FlexRootTypes"),
    "typings": "flext.typings",
    "u": ("flext.utilities", "FlextRootUtilities"),
    "utilities": "flext.utilities",
    "workspace": "flext.workspace",
    "x": "flext_core",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
